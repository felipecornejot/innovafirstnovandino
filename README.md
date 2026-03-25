# Novandino | IP & FTO Executive Dashboard

Dashboard ejecutivo en **Streamlit** para revisar de forma simple, visual y dinámica el estado de:
- vigilancia tecnológica,
- patentabilidad preliminar,
- libertad de operación (FTO),
- familias críticas,
- claim charts,
- y calidad de la base estructurada.

La interfaz combina la lógica gráfica de **Innovafirst** con acentos visuales compatibles con la marca **Novandino**.

## Estructura recomendada del repositorio

```text
novandino-ip-fto-dashboard/
├── app_p1_1.py
├── requirements.txt
├── README.md
├── data/
│   ├── Innovafirst_Matriz_Maestra_Patentes_Consolidada_Fase2.xlsx
│   ├── Innovafirst_Screening_Amplio_Exhaustivo_Razonable_Fase2.xlsx
│   ├── Innovafirst_Dashboard_FTO_Consolidado_Multijurisdiccion.xlsx
│   ├── Innovafirst_ClaimChart_Profundo_Albemarle_US11219863.xlsx
│   └── Innovafirst_ClaimChart_Profundo_Tier1_Complemento.xlsx
└── assets/
    └── novandino_logo.png
```

## Archivos Excel que usará el dashboard

Deja los Excel **con exactamente estos nombres** dentro de `/data`:

1. `Innovafirst_Matriz_Maestra_Patentes_Consolidada_Fase2.xlsx`
2. `Innovafirst_Screening_Amplio_Exhaustivo_Razonable_Fase2.xlsx`
3. `Innovafirst_Dashboard_FTO_Consolidado_Multijurisdiccion.xlsx`
4. `Innovafirst_ClaimChart_Profundo_Albemarle_US11219863.xlsx`
5. `Innovafirst_ClaimChart_Profundo_Tier1_Complemento.xlsx`

### Opcional
Si quieres mostrar el logo en el encabezado, agrega en `/assets`:
- `novandino_logo.png`

## Qué hace el dashboard

### Resumen ejecutivo
Muestra:
- familias identificadas,
- jurisdicciones cubiertas,
- familias en rojo / ámbar,
- señales de estatus activo,
- recomendación ejecutiva automática.

### Riesgo FTO por jurisdicción
Muestra:
- semáforo por país,
- ranking de familias activas por territorio,
- vista acumulada de riesgo.

### Familias y portafolio activo
Muestra:
- ranking de familias,
- titulares,
- módulos,
- acciones recomendadas,
- prioridad de seguimiento.

### Claim charts y trazabilidad
Permite:
- seleccionar una familia,
- revisar filas con claims,
- ver fuentes, hojas y estatus relacionados.

### Salud de datos y control
Permite:
- revisar qué archivos cargaron correctamente,
- ver cobertura de campos,
- explorar hojas y tablas.

## Instalación local

### Crear entorno virtual
```bash
python -m venv .venv
source .venv/bin/activate
```

En Windows PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Instalar dependencias
```bash
pip install -r requirements.txt
```

## Ejecutar en local

```bash
streamlit run app_p1_1.py
```

## Despliegue en GitHub + Streamlit Cloud

### Paso 1
Sube a GitHub:
- `app_p1_1.py`
- `requirements.txt`
- `README.md`
- carpeta `/data` con los Excel
- carpeta `/assets` con `novandino_logo.png` si deseas usarlo

### Paso 2
En Streamlit Community Cloud:
- conecta el repositorio,
- selecciona la rama principal,
- define como archivo principal: `app_p1_1.py`

### Paso 3
Deploy.

## Recomendaciones de calidad de datos

Para que el dashboard funcione mejor:
- mantener consistencia de nombres de columnas,
- no cambiar arbitrariamente los nombres de los archivos,
- preferir hojas estructuradas,
- incluir columnas como:
  - family / familia
  - jurisdiction / country / país
  - risk / riesgo
  - status / estado
  - action / recommendation
  - assignee / titular
  - module / módulo
  - claim / reivindicación

## Roadmap sugerido de mejora

1. Exportar la shortlist crítica a Excel.
2. Exportar la hoja de ruta a Excel para incorporarla al dashboard.
3. Consolidar IDs únicos por familia.
4. Migrar de Excel a Parquet o SQLite cuando la estructura esté estable.
5. Añadir autenticación si se publicará fuera de entorno cerrado.

## Nota
Este dashboard está pensado para **gerencia, comité o directorio**, no para reemplazar el análisis jurídico detallado. Su foco es:
- lectura simple,
- decisión rápida,
- trazabilidad mínima,
- y navegación elegante sobre la base estructurada existente.
