# Novandino | Executive IP Dashboard v2.1

Versión corregida del dashboard ejecutivo.

## Correcciones incluidas
- fuerza el texto del sidebar en blanco para mejorar legibilidad;
- ignora hojas narrativas o de metadata que antes contaminaban la carga;
- filtra filas tipo "Base utilizada", "Criterio rector", "Objetivo", "Resultado", "Estado", "ID", "nan", etc.;
- mejora el llenado de gráficos y tablas ejecutivas.

## Archivo principal
Ejecutar:
```bash
streamlit run app_p2_1.py
```

## Archivos requeridos en `/data`
- Innovafirst_Matriz_Maestra_Patentes_Consolidada_Fase2.xlsx
- Innovafirst_Screening_Amplio_Exhaustivo_Razonable_Fase2.xlsx
- Innovafirst_Dashboard_FTO_Consolidado_Multijurisdiccion.xlsx
- Innovafirst_ClaimChart_Profundo_Albemarle_US11219863.xlsx
- Innovafirst_ClaimChart_Profundo_Tier1_Complemento.xlsx

## Activo opcional en `/assets`
- novandino_logo.png
