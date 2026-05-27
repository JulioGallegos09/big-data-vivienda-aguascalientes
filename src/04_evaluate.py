import math
import pandas as pd

from project_paths import DATA_PROCESSED, FIGURES, MODELS, RESULTS, ensure_dirs


WIDTH = 900
HEIGHT = 560
MARGIN = 70


def svg_header(title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{WIDTH / 2}" y="34" text-anchor="middle" font-family="Arial" font-size="24" font-weight="700">{title}</text>',
    ]


def svg_footer() -> str:
    return "</svg>\n"


def scale(value, src_min, src_max, dst_min, dst_max):
    if src_max == src_min:
        return (dst_min + dst_max) / 2
    return dst_min + (value - src_min) * (dst_max - dst_min) / (src_max - src_min)


def write_svg(path, elements):
    path.write_text("\n".join(elements) + "\n" + svg_footer(), encoding="utf-8")


def axes(elements, x_label, y_label):
    x0, y0 = MARGIN, HEIGHT - MARGIN
    x1, y1 = WIDTH - MARGIN, MARGIN
    elements.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="#222" stroke-width="1.5"/>')
    elements.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="#222" stroke-width="1.5"/>')
    elements.append(f'<text x="{WIDTH / 2}" y="{HEIGHT - 20}" text-anchor="middle" font-family="Arial" font-size="15">{x_label}</text>')
    elements.append(f'<text x="20" y="{HEIGHT / 2}" text-anchor="middle" font-family="Arial" font-size="15" transform="rotate(-90 20 {HEIGHT / 2})">{y_label}</text>')


def save_distribution(df: pd.DataFrame) -> None:
    values = df["price_mxn"].tolist()
    bins = 18
    min_v, max_v = min(values), max(values)
    step = (max_v - min_v) / bins
    counts = [0] * bins
    for value in values:
        idx = min(bins - 1, int((value - min_v) / step))
        counts[idx] += 1

    elements = svg_header("Distribucion de precios de vivienda")
    axes(elements, "Precio (MXN)", "Frecuencia")
    max_count = max(counts)
    bar_w = (WIDTH - 2 * MARGIN) / bins
    for i, count in enumerate(counts):
        h = scale(count, 0, max_count, 0, HEIGHT - 2 * MARGIN)
        x = MARGIN + i * bar_w + 2
        y = HEIGHT - MARGIN - h
        elements.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w - 4:.1f}" height="{h:.1f}" fill="#2f6f8f"/>')
    write_svg(FIGURES / "price_distribution.svg", elements)


def save_map(df: pd.DataFrame) -> None:
    elements = svg_header("Propiedades en Aguascalientes")
    axes(elements, "Longitud", "Latitud")
    min_lon, max_lon = df["longitude"].min(), df["longitude"].max()
    min_lat, max_lat = df["latitude"].min(), df["latitude"].max()
    min_price, max_price = df["price_mxn"].min(), df["price_mxn"].max()
    for _, row in df.iterrows():
        x = scale(row["longitude"], min_lon, max_lon, MARGIN, WIDTH - MARGIN)
        y = scale(row["latitude"], min_lat, max_lat, HEIGHT - MARGIN, MARGIN)
        r = scale(row["built_area_m2"], df["built_area_m2"].min(), df["built_area_m2"].max(), 4, 14)
        shade = int(scale(row["price_mxn"], min_price, max_price, 80, 210))
        color = f"rgb({shade},110,{230 - shade // 2})"
        elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{color}" opacity="0.72" stroke="#fff"/>')
    write_svg(FIGURES / "property_map.svg", elements)


def save_correlation(df: pd.DataFrame) -> None:
    cols = [
        "price_mxn",
        "built_area_m2",
        "land_area_m2",
        "bedrooms",
        "bathrooms",
        "parking_spaces",
        "age_years",
        "distance_to_center_km",
        "amenities_1km",
    ]
    corr = df[cols].corr()
    elements = svg_header("Correlacion de variables numericas")
    grid_size = min(WIDTH - 180, HEIGHT - 140)
    cell = grid_size / len(cols)
    x0, y0 = 150, 80
    for i, row_name in enumerate(cols):
        elements.append(f'<text x="{x0 - 8}" y="{y0 + i * cell + cell / 2 + 5:.1f}" text-anchor="end" font-family="Arial" font-size="11">{row_name}</text>')
        elements.append(f'<text x="{x0 + i * cell + cell / 2:.1f}" y="{y0 - 8}" text-anchor="middle" font-family="Arial" font-size="10" transform="rotate(-45 {x0 + i * cell + cell / 2:.1f} {y0 - 8})">{row_name}</text>')
        for j, col_name in enumerate(cols):
            value = corr.loc[row_name, col_name]
            red = int(scale(value, -1, 1, 60, 210))
            blue = int(scale(value, -1, 1, 210, 60))
            color = f"rgb({red},110,{blue})"
            x = x0 + j * cell
            y = y0 + i * cell
            elements.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" fill="{color}" stroke="#fff"/>')
            elements.append(f'<text x="{x + cell / 2:.1f}" y="{y + cell / 2 + 4:.1f}" text-anchor="middle" font-family="Arial" font-size="10">{value:.2f}</text>')
    write_svg(FIGURES / "correlation_heatmap.svg", elements)


def save_predictions(predictions: pd.DataFrame, metrics: pd.DataFrame) -> None:
    best_model = metrics.sort_values("mae").iloc[0]["model"]
    pred_col = f"{best_model}_predicted_mxn"
    actual = predictions["actual_price_mxn"]
    predicted = predictions[pred_col]
    residuals = actual - predicted

    elements = svg_header(f"Reales vs predichos ({best_model})")
    axes(elements, "Precio real (MXN)", "Precio predicho (MXN)")
    min_v = min(actual.min(), predicted.min())
    max_v = max(actual.max(), predicted.max())
    elements.append(f'<line x1="{MARGIN}" y1="{HEIGHT - MARGIN}" x2="{WIDTH - MARGIN}" y2="{MARGIN}" stroke="#444" stroke-dasharray="7 5"/>')
    for a, p in zip(actual, predicted):
        x = scale(a, min_v, max_v, MARGIN, WIDTH - MARGIN)
        y = scale(p, min_v, max_v, HEIGHT - MARGIN, MARGIN)
        elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#3b7a57" opacity="0.75"/>')
    write_svg(FIGURES / "actual_vs_predicted.svg", elements)

    elements = svg_header(f"Residuales ({best_model})")
    axes(elements, "Precio predicho (MXN)", "Residual")
    min_r, max_r = residuals.min(), residuals.max()
    zero_y = scale(0, min_r, max_r, HEIGHT - MARGIN, MARGIN)
    elements.append(f'<line x1="{MARGIN}" y1="{zero_y:.1f}" x2="{WIDTH - MARGIN}" y2="{zero_y:.1f}" stroke="#444" stroke-dasharray="7 5"/>')
    for p, r in zip(predicted, residuals):
        x = scale(p, predicted.min(), predicted.max(), MARGIN, WIDTH - MARGIN)
        y = scale(r, min_r, max_r, HEIGHT - MARGIN, MARGIN)
        elements.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#b3541e" opacity="0.75"/>')
    write_svg(FIGURES / "residuals.svg", elements)


def save_model_comparison(metrics: pd.DataFrame) -> None:
    elements = svg_header("Comparacion de metricas por modelo")
    axes(elements, "Modelo y metrica", "Valor")
    rows = []
    for _, row in metrics.iterrows():
        rows.extend([(row["model"], "MAE", row["mae"]), (row["model"], "RMSE", row["rmse"]), (row["model"], "R2 x 1M", row["r2"] * 1_000_000)])
    max_v = max(v for _, _, v in rows)
    bar_w = (WIDTH - 2 * MARGIN) / len(rows)
    colors = {"MAE": "#2f6f8f", "RMSE": "#b3541e", "R2 x 1M": "#586f7c"}
    for i, (model, metric, value) in enumerate(rows):
        h = scale(value, 0, max_v, 0, HEIGHT - 2 * MARGIN)
        x = MARGIN + i * bar_w + 8
        y = HEIGHT - MARGIN - h
        elements.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w - 16:.1f}" height="{h:.1f}" fill="{colors[metric]}"/>')
        elements.append(f'<text x="{x + (bar_w - 16) / 2:.1f}" y="{HEIGHT - MARGIN + 18}" text-anchor="middle" font-family="Arial" font-size="10">{model[:5]} {metric}</text>')
    write_svg(FIGURES / "model_comparison.svg", elements)


def save_feature_importance() -> None:
    importance_path = RESULTS / "feature_importance.csv"
    if not importance_path.exists():
        return
    importance = pd.read_csv(importance_path).sort_values("importance", ascending=False).head(12)
    elements = svg_header("Importancia de variables - Gradient Boosting")
    axes(elements, "Importancia", "Variable")
    max_v = importance["importance"].max() or 1
    bar_h = (HEIGHT - 2 * MARGIN) / len(importance)
    for i, (_, row) in enumerate(importance.iterrows()):
        width = scale(row["importance"], 0, max_v, 0, WIDTH - 2 * MARGIN - 180)
        y = MARGIN + i * bar_h + 4
        elements.append(f'<text x="{MARGIN}" y="{y + bar_h / 2:.1f}" font-family="Arial" font-size="12">{row["feature"][:28]}</text>')
        elements.append(f'<rect x="{MARGIN + 190}" y="{y:.1f}" width="{width:.1f}" height="{bar_h - 8:.1f}" fill="#586f7c"/>')
    write_svg(FIGURES / "feature_importance.svg", elements)


def main() -> None:
    ensure_dirs()
    df = pd.read_csv(DATA_PROCESSED / "properties_model.csv")
    predictions = pd.read_csv(RESULTS / "predictions.csv")
    metrics = pd.read_csv(RESULTS / "metrics.csv")

    save_distribution(df)
    save_map(df)
    save_correlation(df)
    save_predictions(predictions, metrics)
    save_model_comparison(metrics)
    save_feature_importance()
    print(f"Graficas SVG guardadas en {FIGURES}")


if __name__ == "__main__":
    main()
