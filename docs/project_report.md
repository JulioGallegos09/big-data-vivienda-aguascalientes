# Reporte del proyecto

## Definicion del problema

Se busca estimar el precio de venta/listado de viviendas en Aguascalientes a partir de variables del inmueble y su ubicacion. La variable objetivo es `price_mxn`; por lo tanto, el enfoque correcto es aprendizaje supervisado de regresion.

## Datos y corpus

El corpus se guarda en `data/raw/properties_raw.csv`. El script de colecta intenta usar la API publica de Mercado Libre; cuando no hay resultados suficientes, genera un corpus curado y deterministico con 145 registros iniciales. Despues de limpieza quedan 140 registros en `data/processed/properties_model.csv`.

Variables principales: precio, superficie construida, superficie de terreno, recamaras, banos, estacionamientos, antiguedad, colonia, municipio, coordenadas y tipo de propiedad.

## Limpieza y preprocesamiento

Se eliminaron duplicados por `property_id`, registros sin variables criticas, precios no positivos y valores atipicos por IQR. Los faltantes en variables numericas se imputaron con mediana. Se agregaron variables de ingenieria: precio por metro cuadrado, distancia al centro, amenidades cercanas, escuelas, hospitales, comercios y bandera de propiedad nueva.

## Base de datos

La base normalizada se genera en `data/processed/housing_ags.sqlite` con tablas:

- `properties`
- `locations`
- `amenities`
- `amenity_summary`
- `market_indicators`

## Modelado

Se comparan dos algoritmos:

- Ridge Regression como baseline lineal.
- Gradient Boosting con stumps de regresion como modelo no lineal.

La particion es 80/20 con semilla fija para reproducibilidad. Las metricas se calculan en datos no vistos.

## Resultados actuales

Resultados de la corrida validada:

| Modelo | MAE | RMSE | R2 |
|---|---:|---:|---:|
| Ridge | 218009.93 | 251136.19 | 0.9404 |
| Gradient Boosting | 315393.98 | 370550.18 | 0.8703 |

En esta corrida, Ridge obtiene menor error. Esto puede ocurrir porque el corpus curado fue generado con una relacion de precio principalmente lineal con superficie, ubicacion y atributos basicos.

## Interpretacion

Un MAE aproximado de 218 mil MXN significa que, en promedio, el modelo baseline se equivoca por esa cantidad contra el precio observado/listado. Para un usuario o negocio inmobiliario, el modelo sirve como estimador inicial y comparador de precios, no como aval profesional.

## Limitaciones y mejoras

- Los precios son de listado o corpus curado, no precios notariales de cierre.
- La disponibilidad de APIs publicas puede cambiar.
- Las amenidades se aproximan por coordenadas y conteos cercanos.
- Se puede mejorar integrando datos reales descargados manualmente, mas ciudades, validacion temporal y modelos adicionales.
