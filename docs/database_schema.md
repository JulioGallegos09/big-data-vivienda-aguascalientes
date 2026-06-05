# Esquema de base de datos normalizada

La base normalizada se entrega en `data/processed/housing_ags.sqlite`.

## Tablas

| Tabla | Llave principal o referencia | Contenido |
|---|---|---|
| `properties` | `property_id` | Atributos principales del inmueble, precio objetivo, variables categoricas y variables de ingenieria no geograficas. |
| `locations` | `property_id` | Colonia, municipio, estado, coordenadas y distancia al centro de Aguascalientes. |
| `amenities` | `amenity_id` | Catalogo de amenidades de referencia usadas para crear variables geoespaciales. |
| `amenity_summary` | `property_id` | Conteos de amenidades, escuelas, hospitales y comercios cercanos por inmueble. |
| `market_indicators` | `indicator_id` | Metadatos de alcance y objetivo del mercado usado en el proyecto. |

## Normalizacion aplicada

- Los datos crudos se conservan en `data/raw/properties_raw.csv`.
- La tabla modelable limpia se conserva en `data/processed/properties_model.csv`.
- La base SQLite separa atributos de propiedad, ubicacion, catalogo de amenidades y resumen de amenidades para evitar mezclar toda la informacion en una sola tabla plana.
- Las transformaciones aplicadas incluyen eliminacion de duplicados, tratamiento de faltantes, filtrado de atipicos por IQR e ingenieria de variables geoespaciales.
