# Entregables para revision

Repositorio GitHub: https://github.com/Gabriel24012/big-data-vivienda-aguascalientes

## Archivos principales

| Entregable solicitado | Archivo o carpeta | Estado |
|---|---|---|
| Archivo con variables | `docs/variables.csv` y `docs/data_dictionary.md` | Listo |
| Base de datos normalizada | `data/processed/housing_ags.sqlite` y `docs/database_schema.md` | Listo |
| Planteamiento de regresion | `README.md` y `docs/project_report.md` | Listo |
| EDA y tipos de variables | `docs/eda_summary.md` y `results/figures/` | Listo |
| Codigo de entrenamiento | `src/03_train_models.py` | Listo |
| Pruebas MAE y R2 | `results/metrics.csv` | Listo |
| Resultados comparativos | `results/metrics.csv` y `results/figures/model_comparison.svg` | Listo |
| GitHub | `git remote origin` apunta al repositorio indicado | Listo |
| Grafica reales vs predichos | `results/figures/actual_vs_predicted.svg` | Listo |
| Grafica de residuales | `results/figures/residuals.svg` | Listo |

## Resultados actuales

| Modelo | MAE | RMSE | R2 | Hiperparametros |
|---|---:|---:|---:|---|
| Ridge | 218009.93 | 251136.19 | 0.9404 | `alpha=10.0` |
| Gradient Boosting | 315393.98 | 370550.18 | 0.8703 | `n_estimators=180`, `learning_rate=0.08` |

El mejor modelo de esta corrida es Ridge, porque logra menor MAE y mayor R2 en el conjunto de prueba.

## Como ejecutar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/00_run_pipeline.py
python src/05_validate_outputs.py
```

## Carpeta sugerida para revisar

- `data/raw/`: datos de entrada.
- `data/processed/`: datos limpios, CSV modelable y SQLite normalizado.
- `src/`: codigo reproducible de colecta, limpieza, entrenamiento, evaluacion y validacion.
- `results/`: metricas, predicciones, importancia de variables y graficas.
- `models/`: modelos entrenados.
- `docs/`: fuentes, variables, esquema, reporte y checklist.
