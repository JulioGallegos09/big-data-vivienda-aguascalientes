import json
import pickle

import numpy as np
import pandas as pd

from project_paths import DATA_PROCESSED, MODELS, RESULTS, ensure_dirs


TARGET = "price_mxn"
DROP_COLUMNS = [
    "property_id",
    "source",
    "title",
    "operation",
    "listing_date",
    "price_per_m2",
    "log_price_mxn",
]


class RidgeRegressor:
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.coef_ = None

    def fit(self, x: np.ndarray, y: np.ndarray):
        x_bias = np.c_[np.ones(len(x)), x]
        identity = np.eye(x_bias.shape[1])
        identity[0, 0] = 0
        self.coef_ = np.linalg.pinv(x_bias.T @ x_bias + self.alpha * identity) @ x_bias.T @ y
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        x_bias = np.c_[np.ones(len(x)), x]
        return x_bias @ self.coef_


class DecisionStump:
    def __init__(self):
        self.feature_index = 0
        self.threshold = 0.0
        self.left_value = 0.0
        self.right_value = 0.0

    def fit(self, x: np.ndarray, residual: np.ndarray):
        best_error = float("inf")
        for feature_index in range(x.shape[1]):
            thresholds = np.unique(np.percentile(x[:, feature_index], [10, 25, 50, 75, 90]))
            for threshold in thresholds:
                left_mask = x[:, feature_index] <= threshold
                right_mask = ~left_mask
                if left_mask.sum() == 0 or right_mask.sum() == 0:
                    continue
                left_value = residual[left_mask].mean()
                right_value = residual[right_mask].mean()
                pred = np.where(left_mask, left_value, right_value)
                error = np.mean((residual - pred) ** 2)
                if error < best_error:
                    best_error = error
                    self.feature_index = feature_index
                    self.threshold = float(threshold)
                    self.left_value = float(left_value)
                    self.right_value = float(right_value)
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        return np.where(x[:, self.feature_index] <= self.threshold, self.left_value, self.right_value)


class GradientBoostingStumps:
    def __init__(self, n_estimators: int = 160, learning_rate: float = 0.06):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.init_value = 0.0
        self.estimators = []
        self.feature_importances_ = None

    def fit(self, x: np.ndarray, y: np.ndarray):
        self.init_value = float(np.mean(y))
        prediction = np.full(len(y), self.init_value)
        importance = np.zeros(x.shape[1])
        self.estimators = []

        for _ in range(self.n_estimators):
            residual = y - prediction
            stump = DecisionStump().fit(x, residual)
            update = stump.predict(x)
            prediction += self.learning_rate * update
            self.estimators.append(stump)
            importance[stump.feature_index] += np.var(update)

        total = importance.sum()
        self.feature_importances_ = importance / total if total else importance
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        prediction = np.full(len(x), self.init_value)
        for stump in self.estimators:
            prediction += self.learning_rate * stump.predict(x)
        return prediction


def make_features(df: pd.DataFrame):
    feature_cols = [c for c in df.columns if c not in DROP_COLUMNS + [TARGET]]
    x = df[feature_cols].copy()
    for col in x.select_dtypes(include=["number"]).columns:
        x[col] = x[col].fillna(x[col].median())
    for col in x.select_dtypes(exclude=["number"]).columns:
        x[col] = x[col].fillna("desconocido")
    x = pd.get_dummies(x, drop_first=False)
    return x.astype(float), x.columns.tolist()


def train_test_split_manual(x: pd.DataFrame, y: pd.Series, test_size: float = 0.2, seed: int = 42):
    rng = np.random.default_rng(seed)
    indices = np.arange(len(x))
    rng.shuffle(indices)
    test_count = int(round(len(x) * test_size))
    test_idx = indices[:test_count]
    train_idx = indices[test_count:]
    return x.iloc[train_idx], x.iloc[test_idx], y.iloc[train_idx], y.iloc[test_idx]


def standardize(train: pd.DataFrame, test: pd.DataFrame):
    means = train.mean()
    stds = train.std().replace(0, 1).fillna(1)
    return ((train - means) / stds).to_numpy(), ((test - means) / stds).to_numpy(), means, stds


def mae(y_true, y_pred):
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true, y_pred):
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def r2(y_true, y_pred):
    denominator = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1 - np.sum((y_true - y_pred) ** 2) / denominator)


def evaluate(name, model, x_test, y_test):
    pred = model.predict(x_test)
    return {"model": name, "mae": mae(y_test, pred), "rmse": rmse(y_test, pred), "r2": r2(y_test, pred)}, pred


def serialize_model(model):
    if isinstance(model, RidgeRegressor):
        return {"type": "ridge", "alpha": model.alpha, "coef": model.coef_.tolist()}
    return {
        "type": "gradient_boosting_stumps",
        "n_estimators": model.n_estimators,
        "learning_rate": model.learning_rate,
        "init_value": model.init_value,
        "feature_importances": model.feature_importances_.tolist(),
        "stumps": [
            {
                "feature_index": stump.feature_index,
                "threshold": stump.threshold,
                "left_value": stump.left_value,
                "right_value": stump.right_value,
            }
            for stump in model.estimators
        ],
    }


def main() -> None:
    ensure_dirs()
    data_path = DATA_PROCESSED / "properties_model.csv"
    if not data_path.exists():
        raise FileNotFoundError("Ejecuta primero src/02_clean_features.py")

    df = pd.read_csv(data_path)
    x, feature_names = make_features(df)
    y = df[TARGET].astype(float)
    x_train, x_test, y_train, y_test = train_test_split_manual(x, y)
    x_train_np, x_test_np, means, stds = standardize(x_train, x_test)
    y_train_np = y_train.to_numpy()
    y_test_np = y_test.to_numpy()

    candidates = [
        ("ridge", RidgeRegressor(alpha=0.1), {"alpha": 0.1}),
        ("ridge", RidgeRegressor(alpha=1.0), {"alpha": 1.0}),
        ("ridge", RidgeRegressor(alpha=10.0), {"alpha": 10.0}),
        ("gradient_boosting", GradientBoostingStumps(n_estimators=120, learning_rate=0.05), {"n_estimators": 120, "learning_rate": 0.05}),
        ("gradient_boosting", GradientBoostingStumps(n_estimators=180, learning_rate=0.05), {"n_estimators": 180, "learning_rate": 0.05}),
        ("gradient_boosting", GradientBoostingStumps(n_estimators=180, learning_rate=0.08), {"n_estimators": 180, "learning_rate": 0.08}),
    ]

    best_by_model = {}
    for name, model, params in candidates:
        model.fit(x_train_np, y_train_np)
        result, _ = evaluate(name, model, x_test_np, y_test_np)
        result["best_params"] = json.dumps(params)
        if name not in best_by_model or result["mae"] < best_by_model[name][0]["mae"]:
            best_by_model[name] = (result, model, params)

    metrics = []
    predictions = pd.DataFrame({"actual_price_mxn": y_test_np})
    fitted_models = {}
    for name, (result, model, params) in best_by_model.items():
        metrics.append(result)
        predictions[f"{name}_predicted_mxn"] = model.predict(x_test_np)
        payload = {
            "model": serialize_model(model),
            "feature_names": feature_names,
            "means": means.to_dict(),
            "stds": stds.to_dict(),
            "params": params,
        }
        fitted_models[name] = payload
        with (MODELS / f"{name}.pkl").open("wb") as model_file:
            pickle.dump(payload, model_file)

    metrics_df = pd.DataFrame(metrics).sort_values("mae")
    metrics_df.to_csv(RESULTS / "metrics.csv", index=False)
    predictions.to_csv(RESULTS / "predictions.csv", index=False)

    gb_payload = fitted_models["gradient_boosting"]
    pd.DataFrame(
        {
            "feature": gb_payload["feature_names"],
            "importance": gb_payload["model"]["feature_importances"],
        }
    ).sort_values("importance", ascending=False).to_csv(RESULTS / "feature_importance.csv", index=False)

    best_name = metrics_df.iloc[0]["model"]
    with (MODELS / "best_model.pkl").open("wb") as model_file:
        pickle.dump(fitted_models[best_name], model_file)

    print(metrics_df.to_string(index=False))


if __name__ == "__main__":
    main()
