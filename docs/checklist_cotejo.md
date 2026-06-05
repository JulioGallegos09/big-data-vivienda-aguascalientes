# Revision contra lista de cotejo

Puntaje total de la lista: 170 puntos. Con la evidencia actual, el proyecto cubre todos los criterios tecnicos. La unica observacion operativa es que el evaluador debe instalar dependencias con `pip install -r requirements.txt` antes de ejecutar los scripts.

| Criterio | Puntaje | Cumple | Evidencia |
|---|---:|---|---|
| 1.1 Fuente de datos: origen, formato y tamano | 5 | Si | `docs/data_sources.md`, `data/raw/properties_raw.csv` |
| 1.2 EDA: estadisticas descriptivas y tipos | 10 | Si | `docs/eda_summary.md`, `results/figures/price_distribution.svg`, `results/figures/correlation_heatmap.svg`, `results/figures/property_map.svg` |
| 1.3 Faltantes, duplicados y atipicos | 10 | Si | `src/02_clean_features.py`, `docs/project_report.md` |
| 1.4 Preprocesamiento adecuado | 10 | Si | `src/02_clean_features.py`, `src/03_train_models.py` |
| 2.1 Datos organizados en estructura apropiada | 5 | Si | `data/raw/properties_raw.csv`, `data/processed/properties_model.csv`, `data/processed/housing_ags.sqlite` |
| 2.2 Base refleja transformaciones | 5 | Si | `data/processed/housing_ags.sqlite`, `docs/database_schema.md` |
| 3.1 Problema definido con objetivo medible | 10 | Si | `README.md`, `docs/project_report.md` |
| 3.2 Justificacion del enfoque y algoritmos | 10 | Si | `README.md`, `docs/project_report.md`, `src/03_train_models.py` |
| 3.3 Hipotesis antes del modelado | 5 | Si | `README.md` |
| 4.1 Codigo estructurado y reproducible | 10 | Si | `src/00_run_pipeline.py`, scripts numerados, `requirements.txt` |
| 4.2 Algoritmo principal implementado | 10 | Si | `src/03_train_models.py` |
| 4.3 Particion train/test | 5 | Si | `src/03_train_models.py` |
| 4.4 Mejora por hiperparametros | 5 | Si | `src/03_train_models.py`, `results/metrics.csv` |
| 5.1 Metricas apropiadas | 10 | Si | `results/metrics.csv` con MAE, RMSE y R2 |
| 5.2 Validacion con datos no vistos | 10 | Si | `src/03_train_models.py`, `results/predictions.csv` |
| 5.3 Comparacion de modelos | 5 | Si | Ridge vs Gradient Boosting en `results/metrics.csv` |
| 6.1 Graficas relevantes y etiquetadas | 5 | Si | `results/figures/*.svg` |
| 6.2 Graficas propias del proyecto | 10 | Si | `actual_vs_predicted.svg`, `residuals.svg`, `model_comparison.svg` |
| 7.1 README con descripcion, uso y resultados | 5 | Si | `README.md` |
| 7.2 Carpetas organizadas | 5 | Si | `data/`, `notebooks/`, `models/`, `results/`, `src/`, `docs/` |
| 7.3 Commits progresivos | 5 | Si | `git log --oneline` muestra 3 commits: documentacion, pipeline y resultados |
| 8.1 Conclusiones responden al objetivo | 10 | Si | `docs/project_report.md` |
| 8.2 Interpretacion en contexto real | 10 | Si | `docs/project_report.md` |
| 8.3 Limitaciones y mejoras | 5 | Si | `README.md`, `docs/project_report.md` |

Puntaje estimado: 170 / 170.

Calificacion estimada: 100 / 100.
