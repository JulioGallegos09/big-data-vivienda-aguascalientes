import sqlite3

import pandas as pd

from project_paths import DATA_PROCESSED, DATA_RAW, FIGURES, MODELS, RESULTS


REQUIRED_FILES = [
    DATA_RAW / "properties_raw.csv",
    DATA_PROCESSED / "properties_model.csv",
    DATA_PROCESSED / "housing_ags.sqlite",
    RESULTS / "metrics.csv",
    RESULTS / "predictions.csv",
    RESULTS / "feature_importance.csv",
    MODELS / "ridge.pkl",
    MODELS / "gradient_boosting.pkl",
    MODELS / "best_model.pkl",
    FIGURES / "price_distribution.svg",
    FIGURES / "property_map.svg",
    FIGURES / "correlation_heatmap.svg",
    FIGURES / "actual_vs_predicted.svg",
    FIGURES / "residuals.svg",
    FIGURES / "model_comparison.svg",
    FIGURES / "feature_importance.svg",
]


def main() -> None:
    missing = [str(path) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        raise FileNotFoundError("Faltan archivos requeridos:\n" + "\n".join(missing))

    df = pd.read_csv(DATA_PROCESSED / "properties_model.csv")
    assert len(df) >= 100, "Se esperaban al menos 100 registros limpios."
    assert df["property_id"].is_unique, "Hay property_id duplicados."
    assert df["price_mxn"].gt(0).all(), "Hay precios no positivos."
    assert df["built_area_m2"].between(30, 650).all(), "Hay superficies fuera de rango."
    assert not df[["price_mxn", "built_area_m2", "bedrooms", "latitude", "longitude"]].isna().any().any()

    metrics = pd.read_csv(RESULTS / "metrics.csv")
    assert {"mae", "rmse", "r2"}.issubset(metrics.columns), "Faltan metricas."
    assert len(metrics) >= 2, "Se esperaban al menos dos modelos comparados."

    with sqlite3.connect(DATA_PROCESSED / "housing_ags.sqlite") as conn:
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)["name"].tolist()
    expected_tables = {"properties", "locations", "amenities", "amenity_summary", "market_indicators"}
    assert expected_tables.issubset(set(tables)), "Faltan tablas en SQLite."

    print("Validacion completada: archivos, datos, metricas y SQLite correctos.")


if __name__ == "__main__":
    main()
