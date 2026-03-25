# Novandino | Executive IP Dashboard v2

Versión mejorada del dashboard ejecutivo para **vigilancia tecnológica, patentabilidad preliminar y libertad de operación (FTO)**, pensado para que una gerencia pueda revisar el estado del proyecto de forma:

- simple,
- visual,
- elegante,
- dinámica,
- y trazable.

Esta versión combina el lenguaje gráfico de **Innovafirst** con acentos compatibles con la identidad visual de **Novandino**.

---

## 1) Estructura recomendada del repositorio

```text
novandino-ip-fto-dashboard/
├── app_p2_0.py
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

---

## 2) Archivos Excel obligatorios

La app espera estos archivos **con exactamente estos nombres** dentro de `/data`:

1. `Innovafirst_Matriz_Maestra_Patentes_Consolidada_Fase2.xlsx`
2. `Innovafirst_Screening_Amplio_Exhaustivo_Razonable_Fase2.xlsx`
3. `Innovafirst_Dashboard_FTO_Consolidado_Multijurisdiccion.xlsx`
4. `Innovafirst_ClaimChart_Profundo_Albemarle_US11219863.xlsx`
5. `Innovafirst_ClaimChart_Profundo_Tier1_Complemento.xlsx`

### Opcionales para una siguiente iteración
Si más adelante los exportas a Excel estructurado, puedes sumar:
- `Innovafirst_Hoja_de_Ruta_Implementacion.xlsx`
- `Innovafirst_Informe_Preliminar_Patentabilidad.xlsx`
- `Innovafirst_Shortlist_Critica_Consolidada_Post_Screening.xlsx`

---

## 3) Logo

Para mostrar el logo de Novandino en el header, deja este archivo en `/assets`:

- `novandino_logo.png`

---

## 4) Qué mejora esta versión

Respecto de la versión anterior, esta versión:

- mejora la armonía visual con la marca Novandino,
- refuerza la lógica ejecutiva y gerencial,
- mejora el cockpit inicial,
- mejora la lectura territorial,
- mejora el drill-down claim-by-claim,
- y mejora la vista de salud de datos.

### Módulos incluidos
1. **Resumen ejecutivo**
2. **Riesgo FTO por jurisdicción**
3. **Familias activas y ranking**
4. **Claim charts y trazabilidad**
5. **Salud de datos**

---

## 5) Instalación local

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

---

## 6) Ejecutar la aplicación

```bash
streamlit run app_p2_0.py
```

---

## 7) Despliegue en GitHub + Streamlit Cloud

### Subir al repositorio
Debes subir:
- `app_p2_0.py`
- `requirements.txt`
- `README.md`
- carpeta `/data` con los Excel
- carpeta `/assets` con `novandino_logo.png`

### En Streamlit Community Cloud
- conectar el repositorio,
- seleccionar la rama principal,
- definir como archivo principal: `app_p2_0.py`

Deploy.

---

## 8) Recomendaciones para que funcione bien

Para mejores resultados:

- mantener nombres de archivo idénticos,
- no romper la estructura de hojas de los Excel,
- mantener columnas como:
  - family / familia
  - jurisdiction / country / país
  - risk / riesgo
  - status / estado
  - action / recommendation
  - assignee / titular
  - module / módulo
  - claim / reivindicación
- intentar homogeneizar encabezados entre workbooks.

---

## 9) Próxima versión sugerida

La siguiente iteración ideal sería integrar también:

- módulo de **hoja de ruta**,
- módulo de **patentabilidad preliminar**,
- filtros descargables,
- snapshots ejecutivos,
- y autenticación si se publicará fuera de entorno privado.

---

## 10) Nota
Este dashboard no reemplaza el análisis jurídico detallado. Su foco es:

- lectura ejecutiva,
- decisión rápida,
- priorización,
- seguimiento,
- y trazabilidad mínima sobre la base estructurada disponible.
