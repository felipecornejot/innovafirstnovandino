
# Novandino | Executive IP Dashboard v2.3

Versión depurada del dashboard ejecutivo para vigilancia tecnológica, patentabilidad preliminar y FTO.

## Qué cambia respecto de v2.2
- mantiene la capa normalizada como fuente única;
- agrega módulos opcionales de:
  - patentabilidad preliminar
  - hoja de ruta
- endurece la lógica de despliegue y deja más limpio el troubleshooting.

## Archivos incluidos
- `app_p3_1.py`
- `build_normalized_layer_v2.py`
- `README_v3_1.md`
- `requirements_v3_1.txt`

## Estructura recomendada
```text
novandino-ip-fto-dashboard/
├── app_p3_1.py
├── build_normalized_layer_v2.py
├── requirements_v3_1.txt
├── README_v3_1.md
├── data/
│   ├── Innovafirst_Matriz_Maestra_Patentes_Consolidada_Fase2.xlsx
│   ├── Innovafirst_Screening_Amplio_Exhaustivo_Razonable_Fase2.xlsx
│   ├── Innovafirst_Dashboard_FTO_Consolidado_Multijurisdiccion.xlsx
│   ├── Innovafirst_ClaimChart_Profundo_Albemarle_US11219863.xlsx
│   ├── Innovafirst_ClaimChart_Profundo_Tier1_Complemento.xlsx
│   ├── Innovafirst_Hoja_de_Ruta_Implementacion.xlsx               # opcional
│   └── Innovafirst_Informe_Preliminar_Patentabilidad.xlsx         # opcional
├── normalized_data/
│   ├── novandino_records.csv
│   ├── novandino_family_summary.csv
│   ├── novandino_jurisdiction_summary.csv
│   ├── novandino_claims.csv
│   ├── novandino_source_control.csv
│   ├── novandino_roadmap.csv                 # opcional
│   └── novandino_patentability.csv           # opcional
└── assets/
    └── novandino_logo.png
```

## Paso 1
Deja los Excel fuente en `/data`.

### Obligatorios
- `Innovafirst_Matriz_Maestra_Patentes_Consolidada_Fase2.xlsx`
- `Innovafirst_Screening_Amplio_Exhaustivo_Razonable_Fase2.xlsx`
- `Innovafirst_Dashboard_FTO_Consolidado_Multijurisdiccion.xlsx`
- `Innovafirst_ClaimChart_Profundo_Albemarle_US11219863.xlsx`
- `Innovafirst_ClaimChart_Profundo_Tier1_Complemento.xlsx`

### Opcionales
- `Innovafirst_Hoja_de_Ruta_Implementacion.xlsx`
- `Innovafirst_Informe_Preliminar_Patentabilidad.xlsx`

## Paso 2
Construye la capa normalizada:
```bash
python build_normalized_layer_v2.py
```

## Paso 3
Corre Streamlit:
```bash
streamlit run app_p3_1.py
```

## Qué hace el normalizador
Genera siempre:
- `novandino_records.csv`
- `novandino_family_summary.csv`
- `novandino_jurisdiction_summary.csv`
- `novandino_claims.csv`
- `novandino_source_control.csv`

Y si existen los Excel opcionales, además:
- `novandino_roadmap.csv`
- `novandino_patentability.csv`

## Ventajas
- evita depender de hojas narrativas o metadata;
- estabiliza columnas;
- mejora la consistencia de gráficos;
- incorpora módulos vivos opcionales;
- deja la base lista para migrar a Parquet o SQLite.

## Recomendación operativa
Cada vez que actualices algún Excel fuente:
1. reemplázalo en `/data`
2. ejecuta:
```bash
python build_normalized_layer_v2.py
```
3. recarga la app

## Logo
Si quieres mostrar el logo, deja `novandino_logo.png` en `/assets`.
