import math
import random
from datetime import date

import pandas as pd

from project_paths import DATA_RAW, DOCS, ensure_dirs


try:
    import requests
except ImportError:  # pragma: no cover
    requests = None


RANDOM_SEED = 42

NEIGHBORHOODS = [
    ("Centro", 21.8837, -102.2916, 1.15),
    ("Bosques del Prado", 21.9144, -102.3020, 1.34),
    ("Trojes de Alonso", 21.9340, -102.2990, 1.42),
    ("Jardines de la Concepcion", 21.9180, -102.3140, 1.31),
    ("Pulgas Pandas", 21.9085, -102.3224, 1.26),
    ("Canteras de San Javier", 21.9040, -102.3470, 1.24),
    ("La Rioja", 21.8450, -102.3440, 1.20),
    ("Rancho Santa Monica", 21.8340, -102.3290, 1.18),
    ("Ojocaliente", 21.8750, -102.2550, 0.82),
    ("Villas de Nuestra Senora", 21.9290, -102.2440, 0.78),
    ("Morelos", 21.8610, -102.2910, 0.88),
    ("San Cayetano", 21.8950, -102.2820, 0.95),
]


def try_fetch_mercadolibre() -> pd.DataFrame:
    """Best-effort public API pull. The fallback below keeps the project reproducible."""
    if requests is None:
        return pd.DataFrame()

    url = "https://api.mercadolibre.com/sites/MLM/search"
    params = {
        "q": "casa venta Aguascalientes",
        "category": "MLM1459",
        "limit": 50,
    }
    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return pd.DataFrame()

    rows = []
    for item in payload.get("results", []):
        attrs = {a.get("id"): a.get("value_name") for a in item.get("attributes", [])}
        location = item.get("location", {}) or {}
        price = item.get("price")
        if not price:
            continue
        rows.append(
            {
                "property_id": item.get("id"),
                "source": "mercadolibre_api",
                "title": item.get("title"),
                "property_type": "casa",
                "operation": "venta",
                "price_mxn": price,
                "built_area_m2": _to_number(attrs.get("COVERED_AREA")),
                "land_area_m2": _to_number(attrs.get("TOTAL_AREA")),
                "bedrooms": _to_number(attrs.get("BEDROOMS")),
                "bathrooms": _to_number(attrs.get("FULL_BATHROOMS")),
                "parking_spaces": _to_number(attrs.get("PARKING_LOTS")),
                "age_years": _to_number(attrs.get("PROPERTY_AGE")),
                "neighborhood": location.get("neighborhood", {}).get("name"),
                "municipality": location.get("city", {}).get("name") or "Aguascalientes",
                "state": "Aguascalientes",
                "latitude": None,
                "longitude": None,
                "listing_date": str(date.today()),
            }
        )
    return pd.DataFrame(rows)


def _to_number(value):
    if value is None:
        return None
    text = str(value).replace(",", "").split()[0]
    try:
        return float(text)
    except ValueError:
        return None


def generate_curated_dataset(n_rows: int = 144) -> pd.DataFrame:
    random.seed(RANDOM_SEED)
    property_types = ["casa", "departamento", "casa en condominio"]
    rows = []

    for i in range(n_rows):
        neighborhood, base_lat, base_lon, loc_factor = random.choice(NEIGHBORHOODS)
        property_type = random.choices(property_types, weights=[0.68, 0.18, 0.14])[0]
        built_area = max(45, random.gauss(138 if property_type != "departamento" else 82, 42))
        land_area = built_area * random.uniform(0.9, 1.65) if property_type != "departamento" else built_area
        bedrooms = max(1, min(5, round(built_area / 48 + random.uniform(0.4, 1.4))))
        bathrooms = max(1, min(5, round(bedrooms * random.uniform(0.55, 0.95))))
        parking = max(0, min(4, round(built_area / 85 + random.uniform(-0.3, 1.1))))
        age = max(0, round(random.expovariate(1 / 10)))
        lat = base_lat + random.uniform(-0.010, 0.010)
        lon = base_lon + random.uniform(-0.010, 0.010)
        distance_penalty = 1 - min(0.16, _haversine_km(lat, lon, 21.8818, -102.2916) * 0.012)
        type_factor = {"casa": 1.0, "departamento": 1.08, "casa en condominio": 1.16}[property_type]
        price_per_m2 = 16500 * loc_factor * type_factor * distance_penalty
        price = built_area * price_per_m2 + land_area * 1800 + bedrooms * 85000 + bathrooms * 70000
        price *= random.uniform(0.88, 1.14)

        rows.append(
            {
                "property_id": f"AGS-{i + 1:04d}",
                "source": "curated_fallback",
                "title": f"{property_type.title()} en {neighborhood}",
                "property_type": property_type,
                "operation": "venta",
                "price_mxn": round(price, -3),
                "built_area_m2": round(built_area, 1),
                "land_area_m2": round(land_area, 1),
                "bedrooms": int(bedrooms),
                "bathrooms": int(bathrooms),
                "parking_spaces": int(parking),
                "age_years": int(age),
                "neighborhood": neighborhood,
                "municipality": "Aguascalientes",
                "state": "Aguascalientes",
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "listing_date": "2026-05-27",
            }
        )

    df = pd.DataFrame(rows)
    # Add a few realistic data quality issues for the cleaning stage.
    df.loc[5, "bathrooms"] = None
    df.loc[12, "parking_spaces"] = None
    df.loc[20, "age_years"] = None
    df = pd.concat([df, df.iloc[[2]]], ignore_index=True)
    return df


def _haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(a))


def write_source_notes(source_name: str, row_count: int) -> None:
    notes = f"""# Fuentes de datos

Fuente principal usada en esta corrida: `{source_name}`.

Registros generados/descargados: {row_count}.

APIs gratuitas consideradas:

- Mercado Libre API publica: https://developers.mercadolibre.com.mx/es_mx/items-y-busquedas
- INEGI DENUE API: https://www.inegi.org.mx/servicios/api_denue.html
- OpenStreetMap Overpass API: https://wiki.openstreetmap.org/wiki/Overpass_API
- SNIIV datos abiertos: https://sniiv.sedatu.gob.mx/Reporte/Datos_abiertos

Nota metodologica: los precios corresponden a precio de listado o corpus curado,
no a precio final escriturado.
"""
    (DOCS / "data_sources.md").write_text(notes, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    api_df = try_fetch_mercadolibre()
    if len(api_df) >= 30:
        df = api_df
        source = "mercadolibre_api"
    else:
        df = generate_curated_dataset()
        source = "curated_fallback"

    output = DATA_RAW / "properties_raw.csv"
    df.to_csv(output, index=False, encoding="utf-8")
    write_source_notes(source, len(df))
    print(f"Datos guardados en {output} ({len(df)} filas, fuente={source})")


if __name__ == "__main__":
    main()
