import math
import sqlite3

import numpy as np
import pandas as pd

from project_paths import DATA_PROCESSED, DATA_RAW, DOCS, ensure_dirs


CENTER_LAT = 21.8818
CENTER_LON = -102.2916


AMENITIES = [
    ("school", 21.8842, -102.2889, "escuela"),
    ("school", 21.9140, -102.3072, "escuela"),
    ("school", 21.8484, -102.3281, "escuela"),
    ("hospital", 21.8884, -102.2968, "hospital"),
    ("hospital", 21.9058, -102.2855, "hospital"),
    ("hospital", 21.8612, -102.2521, "hospital"),
    ("commerce", 21.8800, -102.2960, "comercio"),
    ("commerce", 21.9232, -102.3135, "comercio"),
    ("commerce", 21.8381, -102.3356, "comercio"),
    ("park", 21.8795, -102.2819, "parque"),
    ("park", 21.9107, -102.3268, "parque"),
    ("park", 21.9342, -102.2522, "parque"),
]


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(a))


def count_amenities(lat: float, lon: float, radius_km: float) -> int:
    return sum(1 for _, a_lat, a_lon, _ in AMENITIES if haversine_km(lat, lon, a_lat, a_lon) <= radius_km)


def count_amenities_by_type(lat: float, lon: float, radius_km: float, amenity_type: str) -> int:
    return sum(
        1
        for current_type, a_lat, a_lon, _ in AMENITIES
        if current_type == amenity_type and haversine_km(lat, lon, a_lat, a_lon) <= radius_km
    )


def remove_outliers_iqr(df: pd.DataFrame, column: str) -> pd.DataFrame:
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return df[(df[column] >= lower) & (df[column] <= upper)].copy()


def clean_properties(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["property_id"]).copy()
    numeric_cols = [
        "price_mxn",
        "built_area_m2",
        "land_area_m2",
        "bedrooms",
        "bathrooms",
        "parking_spaces",
        "age_years",
        "latitude",
        "longitude",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    critical = ["price_mxn", "built_area_m2", "bedrooms", "latitude", "longitude"]
    df = df.dropna(subset=critical)
    df = df[(df["price_mxn"] > 300000) & (df["built_area_m2"].between(30, 650))]
    df = remove_outliers_iqr(df, "price_mxn")
    df = remove_outliers_iqr(df, "built_area_m2")

    fill_medians = ["land_area_m2", "bathrooms", "parking_spaces", "age_years"]
    for col in fill_medians:
        df[col] = df[col].fillna(df[col].median())

    df["bathrooms"] = df["bathrooms"].clip(lower=1)
    df["price_per_m2"] = df["price_mxn"] / df["built_area_m2"]
    df["distance_to_center_km"] = df.apply(
        lambda r: haversine_km(r["latitude"], r["longitude"], CENTER_LAT, CENTER_LON), axis=1
    )
    df["amenities_500m"] = df.apply(lambda r: count_amenities(r["latitude"], r["longitude"], 0.5), axis=1)
    df["amenities_1km"] = df.apply(lambda r: count_amenities(r["latitude"], r["longitude"], 1.0), axis=1)
    df["schools_1km"] = df.apply(lambda r: count_amenities_by_type(r["latitude"], r["longitude"], 1.0, "school"), axis=1)
    df["hospitals_1km"] = df.apply(lambda r: count_amenities_by_type(r["latitude"], r["longitude"], 1.0, "hospital"), axis=1)
    df["commerce_1km"] = df.apply(lambda r: count_amenities_by_type(r["latitude"], r["longitude"], 1.0, "commerce"), axis=1)
    df["log_price_mxn"] = np.log1p(df["price_mxn"])
    df["is_new_property"] = (df["age_years"] <= 3).astype(int)
    return df.reset_index(drop=True)


def write_sqlite(df: pd.DataFrame) -> None:
    db_path = DATA_PROCESSED / "housing_ags.sqlite"
    amenities_df = pd.DataFrame(
        AMENITIES, columns=["amenity_type", "latitude", "longitude", "description"]
    ).reset_index(names="amenity_id")
    indicators = pd.DataFrame(
        [
            {
                "indicator_id": 1,
                "name": "scope",
                "value": "Aguascalientes",
                "source": "Proyecto academico con fuentes abiertas",
            },
            {
                "indicator_id": 2,
                "name": "target",
                "value": "precio de listado",
                "source": "Corpus inmobiliario y fallback curado",
            },
        ]
    )
    locations = df[
        ["property_id", "neighborhood", "municipality", "state", "latitude", "longitude", "distance_to_center_km"]
    ].copy()
    properties = df.drop(columns=["latitude", "longitude", "distance_to_center_km"]).copy()
    amenity_summary = df[
        ["property_id", "amenities_500m", "amenities_1km", "schools_1km", "hospitals_1km", "commerce_1km"]
    ].copy()

    with sqlite3.connect(db_path) as conn:
        properties.to_sql("properties", conn, if_exists="replace", index=False)
        locations.to_sql("locations", conn, if_exists="replace", index=False)
        amenities_df.to_sql("amenities", conn, if_exists="replace", index=False)
        amenity_summary.to_sql("amenity_summary", conn, if_exists="replace", index=False)
        indicators.to_sql("market_indicators", conn, if_exists="replace", index=False)


def write_dictionary(columns) -> None:
    descriptions = {
        "price_mxn": "Precio de venta/listado en pesos mexicanos.",
        "built_area_m2": "Superficie construida en metros cuadrados.",
        "land_area_m2": "Superficie de terreno en metros cuadrados.",
        "bedrooms": "Numero de recamaras.",
        "bathrooms": "Numero de banos.",
        "parking_spaces": "Numero de cajones de estacionamiento.",
        "age_years": "Antiguedad estimada de la propiedad.",
        "distance_to_center_km": "Distancia al centro de Aguascalientes.",
        "amenities_500m": "Amenidades cercanas dentro de 500 metros.",
        "amenities_1km": "Amenidades cercanas dentro de 1 kilometro.",
        "price_per_m2": "Precio dividido entre superficie construida.",
    }
    rows = ["# Diccionario de variables", ""]
    for col in columns:
        rows.append(f"- `{col}`: {descriptions.get(col, 'Variable del corpus procesado.')}")
    (DOCS / "data_dictionary.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    raw_path = DATA_RAW / "properties_raw.csv"
    if not raw_path.exists():
        raise FileNotFoundError("Ejecuta primero src/01_collect_data.py")
    raw = pd.read_csv(raw_path)
    clean = clean_properties(raw)
    output = DATA_PROCESSED / "properties_model.csv"
    clean.to_csv(output, index=False, encoding="utf-8")
    write_sqlite(clean)
    write_dictionary(clean.columns)
    print(f"Datos limpios guardados en {output} ({len(clean)} filas)")


if __name__ == "__main__":
    main()
