# Prediccion de Precios de Vivienda en Aguascalientes

Proyecto final de Big Data Analytics para estimar el precio de venta de propiedades en Aguascalientes mediante regresion supervisada.

## Objetivo

Estimar el precio de listado de una vivienda usando variables del inmueble y de ubicacion: superficie, habitaciones, banos, estacionamientos, tipo de propiedad, coordenadas y amenidades cercanas.

## Planteamiento

El problema se aborda como aprendizaje supervisado de regresion porque la variable objetivo (`price_mxn`) es numerica continua. Se comparan dos enfoques:

- `Ridge Regression`: baseline lineal interpretable.
- `Gradient Boosting` con arboles de decision simples: modelo no lineal para capturar relaciones mas complejas.

Hipotesis:

- A mayor superficie construida, mayor precio.
- La ubicacion y las amenidades cercanas explican parte importante del precio.
- Gradient Boosting debe superar al modelo lineal al capturar relaciones no lineales.

## Fuentes de datos

El proyecto intenta consultar fuentes gratuitas y reproducibles:

- Mercado Libre API publica para anuncios de vivienda, cuando este disponible.
- INEGI DENUE para justificar variables de amenidades cercanas.
- OpenStreetMap/Overpass como alternativa abierta para amenidades geoespaciales.
- SNIIV/SHF como contexto de mercado.

Si la API no responde o no hay red, `src/01_collect_data.py` genera un corpus curado y deterministico de Aguascalientes. Ese fallback mantiene el proyecto ejecutable y documenta que los precios son de listado simulado/curado, no precios notariales de cierre.

## Estructura

```text
data/
  raw/                 Datos originales o fallback curado
  processed/           Datos limpios, features y SQLite
docs/                  Diccionario y fuentes
models/                Modelos entrenados
notebooks/             Espacio para EDA
results/
  figures/             Graficas finales
src/                   Scripts reproducibles
```

## Instalacion

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Si `python` no esta en PATH, se puede usar la ruta de Python disponible en el entorno de Codex.

## Ejecucion

```powershell
python src\01_collect_data.py
python src\02_clean_features.py
python src\03_train_models.py
python src\04_evaluate.py
python src\05_validate_outputs.py
```

Tambien se puede correr todo con:

```powershell
python src\00_run_pipeline.py
```

Salida esperada:

- `data/raw/properties_raw.csv`
- `data/processed/properties_model.csv`
- `data/processed/housing_ags.sqlite`
- `results/metrics.csv`
- `results/predictions.csv`
- graficas en `results/figures`
- modelos en `models/` en formato `.pkl`
- reporte en `docs/project_report.md`

## Resultados

Despues de ejecutar los scripts, revisar:

- `results/metrics.csv`: MAE, RMSE, R2 y mejores hiperparametros.
- `results/figures/actual_vs_predicted.svg`: precios reales vs predichos.
- `results/figures/residuals.svg`: errores del modelo.
- `results/figures/model_comparison.svg`: comparacion de modelos.
- `results/figures/feature_importance.svg`: importancia de variables para Gradient Boosting.

## Limitaciones

- El objetivo predice precio de listado, no precio final de compraventa.
- La cobertura depende de disponibilidad de APIs publicas o del corpus curado.
- Las amenidades se aproximan por coordenadas y conteos cercanos; no sustituyen una valuacion profesional.

## Posibles mejoras

- Expandir a otros estados agregando coordenadas base y consultas por ciudad.
- Integrar un dataset real descargado manualmente de portales abiertos si la API limita resultados.
- Probar modelos adicionales como Random Forest, XGBoost o LightGBM.
- Agregar variables economicas por trimestre si se obtiene serie oficial limpia.
