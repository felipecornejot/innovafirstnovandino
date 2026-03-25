from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Novandino | IP & FTO Executive Dashboard",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#333A47"
CYAN = "#31C1D4"
SOFT = "#F0F0F0"
PINK = "#FFB8D1"
GRAY = "#6D6D6E"
PURPLE = "#4F2ACB"
PURPLE_DARK = "#3C1DAA"
BG = "#F7F8FA"
WHITE = "#FFFFFF"

st.markdown(
    f"""
    <style>
        .stApp {{
            background: linear-gradient(180deg, #fbfcfe 0%, #f5f7fb 100%);
        }}
        .main .block-container {{
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 1450px;
        }}
        .hero {{
            background:
              radial-gradient(circle at top right, rgba(49,193,212,0.16), transparent 22%),
              radial-gradient(circle at left center, rgba(79,42,203,0.10), transparent 28%),
              linear-gradient(135deg, rgba(255,255,255,0.96), rgba(240,240,240,0.96));
            border: 1px solid rgba(51,58,71,0.08);
            border-radius: 24px;
            padding: 1.2rem 1.35rem 1.1rem 1.35rem;
            box-shadow: 0 10px 28px rgba(51,58,71,0.08);
            margin-bottom: 1rem;
        }}
        .hero h1 {{
            font-size: 2.0rem;
            line-height: 1.1;
            color: {NAVY};
            margin: 0 0 0.35rem 0;
            font-weight: 800;
        }}
        .hero p {{
            color: {GRAY};
            margin: 0;
            font-size: 0.98rem;
        }}
        .section-title {{
            color: {NAVY};
            font-size: 1.15rem;
            font-weight: 800;
            margin: 0.5rem 0 0.8rem 0;
        }}
        .kpi-card {{
            background: rgba(255,255,255,0.94);
            border: 1px solid rgba(51,58,71,0.07);
            border-left: 5px solid {CYAN};
            border-radius: 18px;
            padding: 0.9rem 1rem 0.8rem 1rem;
            box-shadow: 0 8px 20px rgba(51,58,71,0.05);
            min-height: 112px;
        }}
        .kpi-card.purple {{ border-left-color: {PURPLE}; }}
        .kpi-card.pink {{ border-left-color: {PINK}; }}
        .kpi-label {{
            color: {GRAY};
            font-size: 0.82rem;
            margin-bottom: 0.25rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }}
        .kpi-value {{
            color: {NAVY};
            font-size: 1.85rem;
            line-height: 1.0;
            font-weight: 800;
        }}
        .kpi-foot {{
            color: {GRAY};
            font-size: 0.82rem;
            margin-top: 0.4rem;
        }}
        .info-box {{
            background: rgba(240,240,240,0.9);
            border-left: 5px solid {CYAN};
            border-radius: 18px;
            padding: 0.9rem 1rem;
            color: {NAVY};
            margin-top: 0.5rem;
        }}
        .decision-box {{
            background: linear-gradient(135deg, rgba(79,42,203,0.08), rgba(49,193,212,0.08));
            border: 1px solid rgba(79,42,203,0.12);
            border-radius: 18px;
            padding: 1rem 1rem 0.85rem 1rem;
            color: {NAVY};
            box-shadow: 0 8px 18px rgba(79,42,203,0.05);
        }}
        .decision-box h3 {{ margin: 0 0 0.4rem 0; font-size: 1rem; color: {PURPLE_DARK}; }}
        .pill {{
            display: inline-block;
            padding: 0.18rem 0.55rem;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.02em;
            margin-right: 0.25rem;
            margin-bottom: 0.2rem;
        }}
        .pill.red {{ background: rgba(255, 107, 107, 0.14); color: #C23B3B; }}
        .pill.yellow {{ background: rgba(255, 200, 87, 0.20); color: #8A6700; }}
        .pill.green {{ background: rgba(80, 200, 120, 0.17); color: #287A39; }}
        .small-note {{ color: {GRAY}; font-size: 0.82rem; margin-top: 0.2rem; }}
        .table-caption {{ color: {GRAY}; font-size: 0.86rem; margin: -0.25rem 0 0.55rem 0; }}
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(51,58,71,0.98), rgba(60,29,170,0.97));
            color: white;
        }}
        section[data-testid="stSidebar"] * {{ color: white !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_DIR = Path(__file__).parent / "data"
ASSETS_DIR = Path(__file__).parent / "assets"
EXPECTED_FILES = {
    "matriz_patentes": "Innovafirst_Matriz_Maestra_Patentes_Consolidada_Fase2.xlsx",
    "screening_amplio": "Innovafirst_Screening_Amplio_Exhaustivo_Razonable_Fase2.xlsx",
    "dashboard_fto": "Innovafirst_Dashboard_FTO_Consolidado_Multijurisdiccion.xlsx",
    "claimchart_core": "Innovafirst_ClaimChart_Profundo_Albemarle_US11219863.xlsx",
    "claimchart_tier1b": "Innovafirst_ClaimChart_Profundo_Tier1_Complemento.xlsx",
}
OPTIONAL_LOGO = "novandino_logo.png"


def snake(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9áéíóúÁÉÍÓÚñÑ]+", "_", text.strip().lower())
    return re.sub(r"_+", "_", text).strip("_")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [snake(str(c)) for c in out.columns]
    return out


def pick_column(df: pd.DataFrame, keywords: List[str]) -> Optional[str]:
    cols = list(df.columns)
    for kw in keywords:
        for col in cols:
            if kw in col:
                return col
    return None


def normalize_risk(value: object) -> str:
    t = str(value).strip().lower() if value is not None else ""
    if not t or t == "nan":
        return "No definido"
    if any(x in t for x in ["alto", "high", "red", "rojo", "critical", "crítico"]):
        return "Alto"
    if any(x in t for x in ["medio", "medium", "amber", "yellow", "amarillo", "moderado"]):
        return "Medio"
    if any(x in t for x in ["bajo", "low", "green", "verde"]):
        return "Bajo"
    if any(x in t for x in ["monitor", "watch", "seguimiento"]):
        return "Monitor"
    return str(value)


def risk_to_num(value: object) -> int:
    value = normalize_risk(value)
    return {"Alto": 3, "Medio": 2, "Bajo": 1, "Monitor": 1, "No definido": 0}.get(value, 0)


@st.cache_data(show_spinner=False)
def load_excel_book(path: Path) -> Dict[str, pd.DataFrame]:
    if not path.exists():
        return {}
    xls = pd.ExcelFile(path)
    return {sheet: normalize_columns(pd.read_excel(path, sheet_name=sheet)) for sheet in xls.sheet_names}


@st.cache_data(show_spinner=False)
def load_all_books() -> Dict[str, Dict[str, pd.DataFrame]]:
    return {k: load_excel_book(DATA_DIR / v) for k, v in EXPECTED_FILES.items()}


def enrich(df: pd.DataFrame, source_file: str, sheet: str) -> pd.DataFrame:
    work = df.copy()
    family_col = pick_column(work, ["family", "familia", "patent_family", "family_name", "patent"])
    jurisdiction_col = pick_column(work, ["jurisdiction", "country", "pais", "país", "territory"])
    risk_col = pick_column(work, ["risk", "riesgo", "semaforo", "semáforo"])
    score_col = pick_column(work, ["score", "puntaje", "ranking", "priority"])
    module_col = pick_column(work, ["module", "modulo", "módulo", "cluster"])
    status_col = pick_column(work, ["status", "estado", "legal_status"])
    action_col = pick_column(work, ["action", "accion", "acción", "recommendation", "recomendacion", "recomendación"])
    assignee_col = pick_column(work, ["assignee", "titular", "owner", "applicant", "company"])
    claim_col = pick_column(work, ["claim", "reivindic"])
    type_col = pick_column(work, ["type", "tipo", "category", "categoria"])

    work["_source_file"] = source_file
    work["_sheet"] = sheet
    work["_family"] = work[family_col].astype(str) if family_col else ""
    work["_jurisdiction"] = work[jurisdiction_col].astype(str) if jurisdiction_col else ""
    work["_risk"] = work[risk_col].map(normalize_risk) if risk_col else "No definido"
    work["_risk_num"] = pd.to_numeric(work[score_col], errors="coerce") if score_col else work["_risk"].map(risk_to_num)
    work["_module"] = work[module_col].astype(str) if module_col else "No definido"
    work["_status"] = work[status_col].astype(str) if status_col else "No definido"
    work["_action"] = work[action_col].astype(str) if action_col else "No definida"
    work["_assignee"] = work[assignee_col].astype(str) if assignee_col else "No definido"
    work["_claim"] = work[claim_col].astype(str) if claim_col else ""
    work["_record_type"] = work[type_col].astype(str) if type_col else sheet
    return work


@st.cache_data(show_spinner=False)
def build_master_table() -> pd.DataFrame:
    books = load_all_books()
    frames = []
    for source_key, content in books.items():
        fname = EXPECTED_FILES[source_key]
        for sheet, df in content.items():
            if df is not None and not df.empty:
                frames.append(enrich(df, fname, sheet))
    if not frames:
        return pd.DataFrame()
    master = pd.concat(frames, ignore_index=True, sort=False)
    master["_risk_num"] = pd.to_numeric(master["_risk_num"], errors="coerce").fillna(master["_risk"].map(risk_to_num)).fillna(0)
    for col in ["_family", "_jurisdiction", "_module", "_status", "_action", "_assignee", "_claim"]:
        master[col] = master[col].fillna("").astype(str).str.strip()
    return master


def build_family_summary(master: pd.DataFrame) -> pd.DataFrame:
    if master.empty:
        return pd.DataFrame()
    m = master[master["_family"] != ""]
    if m.empty:
        return pd.DataFrame()
    agg = (
        m.groupby("_family", dropna=False)
        .agg(
            risk_num=("_risk_num", "max"),
            jurisdictions=("_jurisdiction", lambda s: ", ".join(sorted({x for x in s if x}))),
            assignee=("_assignee", lambda s: next((x for x in s if x and x != "No definido"), "No definido")),
            module=("_module", lambda s: next((x for x in s if x and x != "No definido"), "No definido")),
            status=("_status", lambda s: next((x for x in s if x and x != "No definido"), "No definido")),
            action=("_action", lambda s: next((x for x in s if x and x != "No definida"), "No definida")),
            rows=("_family", "size"),
        )
        .reset_index()
    )
    agg["risk"] = agg["risk_num"].map({3: "Alto", 2: "Medio", 1: "Bajo", 0: "No definido"})
    return agg.sort_values(["risk_num", "rows"], ascending=[False, False])


def build_country_summary(master: pd.DataFrame) -> pd.DataFrame:
    if master.empty:
        return pd.DataFrame()
    m = master[master["_jurisdiction"] != ""]
    if m.empty:
        return pd.DataFrame()
    summary = (
        m.groupby("_jurisdiction")
        .agg(
            total_registros=("_jurisdiction", "size"),
            familias=("_family", lambda s: len({x for x in s if x})),
            riesgo_promedio=("_risk_num", "mean"),
            riesgo_max=("_risk_num", "max"),
            alto=("_risk", lambda s: int((s == "Alto").sum())),
            medio=("_risk", lambda s: int((s == "Medio").sum())),
            bajo=("_risk", lambda s: int((s == "Bajo").sum())),
        )
        .reset_index()
        .sort_values(["riesgo_max", "riesgo_promedio", "familias"], ascending=[False, False, False])
    )
    summary["semaforo"] = summary["riesgo_max"].map({3: "Alto", 2: "Medio", 1: "Bajo", 0: "No definido"})
    return summary


def build_claim_table(master: pd.DataFrame) -> pd.DataFrame:
    if master.empty:
        return pd.DataFrame()
    return master[(master["_claim"] != "") | (master["_sheet"].str.contains("claim", case=False, na=False))].copy()


def get_missing_files() -> List[str]:
    return [fname for fname in EXPECTED_FILES.values() if not (DATA_DIR / fname).exists()]


def recommendation_text(df: pd.DataFrame) -> str:
    if df.empty:
        return "Completar la carga de datos estructurados para habilitar una lectura ejecutiva confiable."
    high = int((df["_risk"] == "Alto").sum())
    medium = int((df["_risk"] == "Medio").sum())
    pending = int(df["_status"].str.contains("pending|verify|pendiente", case=False, na=False).sum())
    if high >= 5:
        return "Priorizar revisión legal externa y diseño-around sobre las familias con riesgo alto antes de cualquier decisión de implementación territorial."
    if high >= 1:
        return "Mantener control de familias críticas activas y cerrar validación fina de jurisdicciones antes de ampliar despliegue o filing."
    if medium >= 5:
        return "Avanzar con monitoreo activo, cierre de brechas técnicas y validación de patentabilidad antes de mover la estrategia territorial."
    if pending >= 3:
        return "Completar verificación de estatus y claims antes de endurecer conclusiones ejecutivas."
    return "El portafolio aparece controlable en esta iteración; conviene consolidar patentabilidad y hoja de ruta IP."


def kpi_card(label: str, value: str, foot: str = "", accent: str = "") -> None:
    cls = "kpi-card"
    if accent == "purple":
        cls += " purple"
    elif accent == "pink":
        cls += " pink"
    st.markdown(
        f"""
        <div class="{cls}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def brand_header() -> None:
    logo_path = ASSETS_DIR / OPTIONAL_LOGO
    left, right = st.columns([1.2, 4])
    with left:
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
    with right:
        st.markdown(
            """
            <div class="hero">
                <h1>Novandino | IP &amp; FTO Executive Dashboard</h1>
                <p>
                    Panel ejecutivo para vigilancia tecnológica, patentabilidad y libertad de operación,
                    con estética Innovafirst y lectura simple para toma de decisiones gerenciales.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def section_filters(master: pd.DataFrame) -> pd.DataFrame:
    jurisdictions = sorted([x for x in master["_jurisdiction"].dropna().unique() if x])
    risks = sorted([x for x in master["_risk"].dropna().unique() if x])
    modules = sorted([x for x in master["_module"].dropna().unique() if x])

    st.sidebar.markdown("### Filtros")
    selected_j = st.sidebar.multiselect("Jurisdicción", jurisdictions)
    selected_r = st.sidebar.multiselect("Riesgo", risks, default=risks)
    selected_m = st.sidebar.multiselect("Módulo", modules)

    filtered = master.copy()
    if selected_j:
        filtered = filtered[filtered["_jurisdiction"].isin(selected_j)]
    if selected_r:
        filtered = filtered[filtered["_risk"].isin(selected_r)]
    if selected_m:
        filtered = filtered[filtered["_module"].isin(selected_m)]
    return filtered


master = build_master_table()
family_summary = build_family_summary(master)
country_summary = build_country_summary(master)
claims_table = build_claim_table(master)
missing_files = get_missing_files()

brand_header()
if master.empty:
    st.error("No se encontraron archivos estructurados en la carpeta /data. Revisa el README y los nombres exactos.")
    st.stop()

if missing_files:
    st.warning("Faltan archivos esperados para la lectura completa del dashboard:")
    for m in missing_files:
        st.write(f"- {m}")

st.sidebar.markdown("## Navegación")
page = st.sidebar.radio(
    "Ir a",
    [
        "Resumen ejecutivo",
        "Riesgo FTO por jurisdicción",
        "Familias y portafolio activo",
        "Claim charts y trazabilidad",
        "Salud de datos y control",
    ],
)
filtered_master = section_filters(master)

if page == "Resumen ejecutivo":
    st.markdown('<div class="section-title">Cockpit ejecutivo</div>', unsafe_allow_html=True)
    total_families = int(family_summary["_family"].nunique()) if not family_summary.empty else 0
    total_countries = int(country_summary["_jurisdiction"].nunique()) if not country_summary.empty else 0
    high_families = int((family_summary["risk"] == "Alto").sum()) if not family_summary.empty else 0
    medium_families = int((family_summary["risk"] == "Medio").sum()) if not family_summary.empty else 0
    active_mentions = int(master["_status"].str.contains("active|vigente|granted|grant", case=False, na=False).sum())
    recommendation = recommendation_text(filtered_master if not filtered_master.empty else master)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("Familias identificadas", f"{total_families}", "Universo estructurado cargado", "purple")
    with c2: kpi_card("Jurisdicciones", f"{total_countries}", "Cobertura territorial visible")
    with c3: kpi_card("Familias en rojo", f"{high_families}", "Riesgo alto FTO", "pink")
    with c4: kpi_card("Familias en ámbar", f"{medium_families}", "Requieren control activo")
    with c5: kpi_card("Menciones activas", f"{active_mentions}", "Estatus con señal activa o concedida")

    left, right = st.columns([1.55, 1])
    with left:
        st.markdown('<div class="section-title">Riesgo por jurisdicción</div>', unsafe_allow_html=True)
        if not country_summary.empty:
            chart = country_summary.head(15).copy()
            fig = px.bar(chart, x="_jurisdiction", y="riesgo_promedio", color="semaforo", text="familias",
                         color_discrete_map={"Alto": PINK, "Medio": CYAN, "Bajo": PURPLE, "No definido": GRAY})
            fig.update_layout(height=390, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              xaxis_title="Jurisdicción", yaxis_title="Riesgo promedio", margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown(f"""
            <div class="decision-box">
                <h3>Recomendación ejecutiva</h3>
                <p>{recommendation}</p>
                <div style="margin-top:0.35rem;">
                    <span class="pill red">Rojo = bloqueo o revisión legal inmediata</span>
                    <span class="pill yellow">Ámbar = monitoreo y diseño-around</span>
                    <span class="pill green">Verde = bajo riesgo relativo</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('<div class="section-title">Top familias activas</div>', unsafe_allow_html=True)
        st.dataframe(family_summary.head(8)[["_family", "risk", "module", "assignee", "action"]], use_container_width=True, hide_index=True)

    b1, b2 = st.columns(2)
    with b1:
        st.markdown('<div class="section-title">Distribución de riesgo</div>', unsafe_allow_html=True)
        risk_counts = family_summary["risk"].value_counts().reset_index()
        risk_counts.columns = ["Riesgo", "Cantidad"]
        fig2 = px.pie(risk_counts, names="Riesgo", values="Cantidad", color="Riesgo",
                      color_discrete_map={"Alto": PINK, "Medio": CYAN, "Bajo": PURPLE, "No definido": GRAY}, hole=0.58)
        fig2.update_layout(height=360, margin=dict(l=0,r=0,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)
    with b2:
        st.markdown('<div class="section-title">Módulos más cargados</div>', unsafe_allow_html=True)
        mod = (master[master["_module"] != ""].groupby("_module").agg(registros=("_module", "size"), riesgo=("_risk_num", "mean")).reset_index().sort_values("registros", ascending=False).head(10))
        fig3 = px.bar(mod, x="registros", y="_module", color="riesgo", orientation="h", color_continuous_scale=[PURPLE, CYAN, PINK])
        fig3.update_layout(height=360, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig3, use_container_width=True)

elif page == "Riesgo FTO por jurisdicción":
    st.markdown('<div class="section-title">Semáforo final por país / jurisdicción</div>', unsafe_allow_html=True)
    if country_summary.empty:
        st.info("No hay columna de jurisdicción suficientemente estructurada en los archivos cargados.")
    else:
        c1, c2 = st.columns([1.2, 1])
        with c1:
            heat = country_summary.copy()
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Alto", x=heat["_jurisdiction"], y=heat["alto"], marker_color=PINK))
            fig.add_trace(go.Bar(name="Medio", x=heat["_jurisdiction"], y=heat["medio"], marker_color=CYAN))
            fig.add_trace(go.Bar(name="Bajo", x=heat["_jurisdiction"], y=heat["bajo"], marker_color=PURPLE))
            fig.update_layout(barmode="stack", height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              xaxis_title="Jurisdicción", yaxis_title="Registros clasificados", margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown('<div class="info-box"><strong>Cómo leer esta vista.</strong><br>La barra apilada combina profundidad y temperatura. Un país con pocas menciones pero alto riesgo máximo puede requerir atención jurídica antes que otro con muchas menciones de baja severidad.</div>', unsafe_allow_html=True)
            st.dataframe(country_summary[["_jurisdiction", "familias", "riesgo_promedio", "riesgo_max", "semaforo"]], use_container_width=True, hide_index=True)
        view = filtered_master.copy()
        view = view[(view["_family"] != "") & (view["_jurisdiction"] != "")]
        slim = view[["_jurisdiction", "_family", "_risk", "_status", "_assignee", "_action", "_source_file"]].drop_duplicates()
        st.markdown('<div class="section-title">Ranking de familias activas por territorio</div>', unsafe_allow_html=True)
        st.dataframe(slim, use_container_width=True, hide_index=True)

elif page == "Familias y portafolio activo":
    st.markdown('<div class="section-title">Ranking final de familias activas y prioridad de seguimiento</div>', unsafe_allow_html=True)
    fam = family_summary.copy()
    search = st.text_input("Buscar familia, titular o módulo")
    if search:
        mask = fam["_family"].str.contains(search, case=False, na=False) | fam["assignee"].str.contains(search, case=False, na=False) | fam["module"].str.contains(search, case=False, na=False)
        fam = fam[mask]
    left, right = st.columns([1.1, 1])
    with left:
        topn = fam.head(15)
        fig = px.bar(topn, x="risk_num", y="_family", color="risk", orientation="h",
                     color_discrete_map={"Alto": PINK, "Medio": CYAN, "Bajo": PURPLE, "No definido": GRAY},
                     hover_data=["assignee", "module", "status", "action"])
        fig.update_layout(height=520, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Puntaje relativo", yaxis_title="Familia")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        holder = fam.groupby("assignee").agg(familias=("_family", "size"), riesgo=("risk_num", "mean")).reset_index().sort_values("familias", ascending=False).head(12)
        fig2 = px.treemap(holder, path=["assignee"], values="familias", color="riesgo", color_continuous_scale=[PURPLE, CYAN, PINK])
        fig2.update_layout(height=520, margin=dict(l=0,r=0,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(fam[["_family", "risk", "assignee", "module", "status", "action", "jurisdictions"]], use_container_width=True, hide_index=True)

elif page == "Claim charts y trazabilidad":
    st.markdown('<div class="section-title">Drill-down claim-by-claim</div>', unsafe_allow_html=True)
    if claims_table.empty:
        st.info("No se detectaron hojas o columnas de claim chart suficientemente estructuradas.")
    else:
        families = sorted([x for x in claims_table["_family"].dropna().unique() if x])
        sel_family = st.selectbox("Seleccionar familia", families)
        sub = claims_table[claims_table["_family"] == sel_family].copy()
        a, b = st.columns([1.3, 1])
        with a:
            cols_show = [c for c in ["_family", "_jurisdiction", "_claim", "_risk", "_status", "_action", "_source_file", "_sheet"] if c in sub.columns]
            st.dataframe(sub[cols_show], use_container_width=True, hide_index=True)
        with b:
            meta = family_summary[family_summary["_family"] == sel_family]
            if not meta.empty:
                row = meta.iloc[0]
                st.markdown(f"""
                    <div class="decision-box">
                        <h3>Ficha rápida de la familia</h3>
                        <p><strong>Riesgo:</strong> {row['risk']}</p>
                        <p><strong>Titular:</strong> {row['assignee']}</p>
                        <p><strong>Módulo:</strong> {row['module']}</p>
                        <p><strong>Estatus:</strong> {row['status']}</p>
                        <p><strong>Acción:</strong> {row['action']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        trace = sub[["_source_file", "_sheet", "_jurisdiction", "_status"]].drop_duplicates()
        st.markdown('<div class="section-title">Trazabilidad de fuentes</div>', unsafe_allow_html=True)
        st.dataframe(trace, use_container_width=True, hide_index=True)

else:
    st.markdown('<div class="section-title">Control de carga y calidad de datos</div>', unsafe_allow_html=True)
    books = load_all_books()
    control_df = pd.DataFrame([
        {"Archivo": fname, "Disponible": "Sí" if (DATA_DIR / fname).exists() else "No", "Hojas leídas": len(books.get(key, {})), "Filas estimadas": int(sum(df.shape[0] for df in books.get(key, {}).values()))}
        for key, fname in EXPECTED_FILES.items()
    ])
    st.dataframe(control_df, use_container_width=True, hide_index=True)
    c1, c2 = st.columns(2)
    with c1:
        completeness = pd.DataFrame([
            {"Campo": "Familia", "Completitud %": round((master["_family"] != "").mean() * 100, 1)},
            {"Campo": "Jurisdicción", "Completitud %": round((master["_jurisdiction"] != "").mean() * 100, 1)},
            {"Campo": "Riesgo", "Completitud %": round((master["_risk"] != "No definido").mean() * 100, 1)},
            {"Campo": "Estatus", "Completitud %": round((master["_status"] != "No definido").mean() * 100, 1)},
            {"Campo": "Acción", "Completitud %": round((master["_action"] != "No definida").mean() * 100, 1)},
        ])
        fig = px.bar(completeness, x="Completitud %", y="Campo", orientation="h", color="Completitud %", color_continuous_scale=[PINK, CYAN, PURPLE])
        fig.update_layout(height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown('''<div class="info-box"><strong>Prioridades de hardening del dashboard</strong><br><br>
            1. Unificar nombres de columnas entre workbooks.<br>
            2. Estandarizar la codificación de riesgo y estatus por jurisdicción.<br>
            3. Exportar shortlist y hoja de ruta en Excel para enriquecer la capa de gestión.<br>
            4. Consolidar un identificador único por familia para evitar dobles conteos.<br>
            5. Versionar la base en formato Parquet cuando el modelo quede estable.
            </div>''', unsafe_allow_html=True)
    sheet_options = sorted(set(master["_source_file"].astype(str) + " | " + master["_sheet"].astype(str)))
    sel = st.selectbox("Elegir origen", sheet_options)
    src_file, src_sheet = [x.strip() for x in sel.split("|", 1)]
    exp = master[(master["_source_file"] == src_file) & (master["_sheet"] == src_sheet)]
    st.dataframe(exp, use_container_width=True, hide_index=True)

st.markdown('<div class="small-note">Diseño visual alineado a Innovafirst y armonizado con acentos Novandino. Para despliegue, cargar los archivos Excel en /data y el logo opcional en /assets/novandino_logo.png.</div>', unsafe_allow_html=True)
