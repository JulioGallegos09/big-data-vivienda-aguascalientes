# Resumen EDA

Registros procesados: 140.
Variables procesadas: 27.

## Tipos de variables

| Variable | Tipo detectado |
|---|---|
| property_id | categorica/texto |
| source | categorica/texto |
| title | categorica/texto |
| property_type | categorica/texto |
| operation | categorica/texto |
| price_mxn | numerica |
| built_area_m2 | numerica |
| land_area_m2 | numerica |
| bedrooms | numerica |
| bathrooms | numerica |
| parking_spaces | numerica |
| age_years | numerica |
| neighborhood | categorica/texto |
| municipality | categorica/texto |
| state | categorica/texto |
| latitude | numerica |
| longitude | numerica |
| listing_date | categorica/texto |
| price_per_m2 | numerica |
| distance_to_center_km | numerica |
| amenities_500m | numerica |
| amenities_1km | numerica |
| schools_1km | numerica |
| hospitals_1km | numerica |
| commerce_1km | numerica |
| log_price_mxn | numerica |
| is_new_property | numerica |

## Estadisticas descriptivas numericas

| Variable | Media | Mediana | Min | Max |
|---|---:|---:|---:|---:|
| price_mxn | 3161500.00 | 3136000.00 | 978000.00 | 5457000.00 |
| built_area_m2 | 132.80 | 131.85 | 45.00 | 228.50 |
| land_area_m2 | 166.27 | 165.60 | 45.00 | 374.90 |
| bedrooms | 3.64 | 4.00 | 2.00 | 5.00 |
| bathrooms | 2.72 | 3.00 | 1.00 | 5.00 |
| parking_spaces | 1.95 | 2.00 | 0.00 | 4.00 |
| age_years | 10.53 | 8.00 | 0.00 | 52.00 |
| latitude | 21.89 | 21.90 | 21.82 | 21.94 |
| longitude | -102.30 | -102.30 | -102.36 | -102.24 |
| price_per_m2 | 24150.56 | 24230.34 | 15153.71 | 33826.71 |
| distance_to_center_km | 4.54 | 4.70 | 0.25 | 8.33 |
| amenities_500m | 0.14 | 0.00 | 0.00 | 1.00 |
| amenities_1km | 0.58 | 0.00 | 0.00 | 3.00 |
| schools_1km | 0.20 | 0.00 | 0.00 | 1.00 |
| hospitals_1km | 0.06 | 0.00 | 0.00 | 1.00 |
| commerce_1km | 0.15 | 0.00 | 0.00 | 1.00 |
| log_price_mxn | 14.91 | 14.96 | 13.79 | 15.51 |
| is_new_property | 0.29 | 0.00 | 0.00 | 1.00 |

## Frecuencias principales

### property_type

| Valor | Conteo |
|---|---:|
| casa | 101 |
| casa en condominio | 20 |
| departamento | 19 |

### neighborhood

| Valor | Conteo |
|---|---:|
| Morelos | 21 |
| Jardines de la Concepcion | 18 |
| Villas de Nuestra Senora | 15 |
| Ojocaliente | 12 |
| Bosques del Prado | 11 |
| Trojes de Alonso | 11 |
| San Cayetano | 10 |
| Canteras de San Javier | 10 |

### municipality

| Valor | Conteo |
|---|---:|
| Aguascalientes | 140 |

### source

| Valor | Conteo |
|---|---:|
| curated_fallback | 140 |
