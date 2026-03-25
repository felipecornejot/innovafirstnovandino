
from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Novandino | Executive IP Dashboard v2.3",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#333A47"
CYAN = "#31C1D4"
PINK = "#FFB8D1"
GRAY = "#6D6D6E"
NOVA_PURPLE = "#4F2ACB"
NOVA_PURPLE_DARK = "#3C1DAA"
RED = "#E16060"
YELLOW = "#D8A22B"
GREEN = "#3B9B6B"

NORMALIZED_DIR = Path(__file__).parent / "normalized_data"
ASSETS_DIR = Path(__file__).parent / "assets"

EXPECTED = {
    "records": "novandino_records.csv",
    "families": "novandino_family_summary.csv",
    "jurisdictions": "novandino_jurisdiction_summary.csv",
    "claims": "novandino_claims.csv",
    "sources": "novandino_source_control.csv",
    "roadmap": "novandino_roadmap.csv",
    "patentability": "novandino_patentability.csv",
}

st.markdown(
    f'''
    <style>
        .stApp {{
            background:
                radial-gradient(circle at top right, rgba(79,42,203,0.08), transparent 18%),
                radial-gradient(circle at left top, rgba(49,193,212,0.10), transparent 20%),
                linear-gradient(180deg, #fafbfe 0%, #f4f7fb 100%);
        }}
        .main .block-container {{
            max-width: 1500px;
            padding-top: 1.15rem;
            padding-bottom: 2rem;
        }}
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(51,58,71,0.98), rgba(60,29,170,0.98));
        }}
        section[data-testid="stSidebar"] * {{
            color: white !important;
        }}
        section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
        section[data-testid="stSidebar"] div[data-baseweb="select"] span {{
            color: white !important;
            background-color: rgba(255,255,255,0.06) !important;
        }}
        .hero {{
            background:
                linear-gradient(120deg, rgba(255,255,255,0.98), rgba(240,240,240,0.96)),
                radial-gradient(circle at top right, rgba(49,193,212,0.08), transparent 20%);
            border: 1px solid rgba(51,58,71,0.08);
            border-radius: 26px;
            box-shadow: 0 14px 30px rgba(51,58,71,0.07);
            padding: 1.15rem 1.35rem 1.05rem 1.35rem;
            margin-bottom: 1rem;
        }}
        .hero-title {{
            color: {NAVY};
            font-size: 2rem;
            font-weight: 900;
            margin: 0 0 0.2rem 0;
            line-height: 1.05;
        }}
        .hero-sub {{
            color: {GRAY};
            font-size: 0.98rem;
            margin: 0;
        }}
        .section-title {{
            color: {NAVY};
            font-size: 1.15rem;
            font-weight: 850;
            margin: 0.35rem 0 0.8rem 0;
        }}
        .subnote {{
            color: {GRAY};
            font-size: 0.85rem;
            margin-top: -0.25rem;
            margin-bottom: 0.65rem;
        }}
        .metric-card {{
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(51,58,71,0.08);
            border-left: 5px solid {CYAN};
            border-radius: 18px;
            padding: 0.9rem 1rem;
            min-height: 114px;
            box-shadow: 0 10px 22px rgba(51,58,71,0.05);
        }}
        .metric-card.purple {{ border-left-color: {NOVA_PURPLE}; }}
        .metric-card.pink {{ border-left-color: {PINK}; }}
        .metric-card.green {{ border-left-color: {GREEN}; }}
        .metric-label {{
            color: {GRAY};
            font-size: 0.78rem;
            text-transform: uppercase;
            font-weight: 800;
            letter-spacing: 0.02em;
            margin-bottom: 0.3rem;
        }}
        .metric-value {{
            color: {NAVY};
            font-size: 1.8rem;
            font-weight: 900;
            line-height: 1.0;
        }}
        .metric-foot {{
            color: {GRAY};
            font-size: 0.82rem;
            margin-top: 0.42rem;
        }}
        .decision-box {{
            background: linear-gradient(135deg, rgba(79,42,203,0.08), rgba(49,193,212,0.08));
            border: 1px solid rgba(79,42,203,0.12);
            border-radius: 18px;
            padding: 1rem 1rem 0.9rem 1rem;
            color: {NAVY};
            box-shadow: 0 10px 24px rgba(79,42,203,0.05);
        }}
        .decision-box h3 {{
            margin: 0 0 0.35rem 0;
            color: {NOVA_PURPLE_DARK};
            font-size: 1rem;
        }}
        .info-box {{
            background: rgba(240,240,240,0.92);
            border-left: 5px solid {CYAN};
            border-radius: 18px;
            padding: 0.9rem 1rem;
            color: {NAVY};
        }}
        .risk-pill {{
            display: inline-block;
            padding: 0.18rem 0.55rem;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 800;
            margin-right: 0.25rem;
            margin-bottom: 0.2rem;
        }}
        .risk-red {{ background: rgba(225,96,96,0.14); color: {RED}; }}
        .risk-yellow {{ background: rgba(216,162,43,0.18); color: {YELLOW}; }}
        .risk-green {{ background: rgba(59,155,107,0.15); color: {GREEN}; }}
        .footer-note {{
            color: {GRAY};
            font-size: 0.82rem;
            margin-top: 1rem;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.4rem;
        }}
        .stTabs [data-baseweb="tab"] {{
            background: rgba(255,255,255,0.92);
            border-radius: 14px;
            padding: 0.5rem 0.9rem;
            border: 1px solid rgba(51,58,71,0.08);
        }}
        .stTabs [aria-selected="true"] {{
            background: rgba(79,42,203,0.10);
            border-color: rgba(79,42,203,0.18);
        }}
    </style>
    ''',
    unsafe_allow_html=True,
)

@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def load_all() -> Dict[str, pd.DataFrame]:
    return {k: load_csv(NORMALIZED_DIR / v) for k, v in EXPECTED.items()}

def recommendation_from_data(df: pd.DataFrame) -> str:
    if df.empty:
        return "La capa normalizada aún no está disponible."
    high = int((df["risk"] == "Alto").sum()) if "risk" in df else 0
    medium = int((df["risk"] == "Medio").sum()) if "risk" in df else 0
    active = int((df["status_bucket"] == "Activo / concedido").sum()) if "status_bucket" in df else 0
    if high >= 8:
        return "Priorizar revisión legal externa y diseño-around antes de cualquier movimiento territorial o filing adicional."
    if high >= 3:
        return "Mantener control activo sobre familias rojas y modular decisiones país por país."
    if medium >= 10 and active >= 5:
        return "El universo requiere monitoreo intensivo, pero parece gestionable con una hoja de ruta disciplinada."
    return "La base normalizada sugiere un escenario controlable; conviene endurecer patentabilidad y hoja de ruta."

def kpi_card(label: str, value: str, foot: str = "", cls: str = "") -> None:
    extra = f" {cls}" if cls else ""
    st.markdown(
        f'''
        <div class="metric-card{extra}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-foot">{foot}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

def header() -> None:
    logo = ASSETS_DIR / "novandino_logo.png"
    c1, c2 = st.columns([1, 4])
    with c1:
        if logo.exists():
            st.image(str(logo), use_container_width=True)
    with c2:
        st.markdown(
            '''
            <div class="hero">
                <div class="hero-title">Novandino | Executive IP Dashboard v2.3</div>
                <p class="hero-sub">
                    Panel gerencial basado exclusivamente en una capa de datos normalizada. Esta versión incorpora módulos de patentabilidad y hoja de ruta, además del core FTO.
                </p>
            </div>
            ''',
            unsafe_allow_html=True,
        )

header()
dfs = load_all()

records = dfs["records"]
families = dfs["families"]
jurisdictions = dfs["jurisdictions"]
claims = dfs["claims"]
sources = dfs["sources"]
roadmap = dfs["roadmap"]
patentability = dfs["patentability"]

required_missing = [EXPECTED[k] for k in ["records", "families", "jurisdictions", "claims", "sources"] if dfs[k].empty]
if required_missing:
    st.error("Faltan archivos normalizados base. Ejecuta primero `build_normalized_layer_v2.py` y verifica la carpeta /normalized_data.")
    for m in required_missing:
        st.write(f"- {m}")
    st.stop()

st.sidebar.markdown("## Navegación")
page = st.sidebar.radio(
    "Ir a",
    [
        "01 Resumen ejecutivo",
        "02 Riesgo FTO por jurisdicción",
        "03 Familias activas y ranking",
        "04 Claim charts y trazabilidad",
        "05 Patentabilidad preliminar",
        "06 Hoja de ruta",
        "07 Salud de datos",
    ],
)

st.sidebar.markdown("## Filtros")
jur_options = sorted([x for x in records["jurisdiction"].dropna().unique().tolist() if str(x).strip()]) if "jurisdiction" in records else []
risk_options = sorted([x for x in records["risk"].dropna().unique().tolist() if str(x).strip()]) if "risk" in records else []
module_options = sorted([x for x in records["module"].dropna().unique().tolist() if str(x).strip()]) if "module" in records else []

sel_jur = st.sidebar.multiselect("Jurisdicción", jur_options)
sel_risk = st.sidebar.multiselect("Riesgo", risk_options, default=risk_options)
sel_mod = st.sidebar.multiselect("Módulo", module_options)

filtered_records = records.copy()
if sel_jur and "jurisdiction" in filtered_records:
    filtered_records = filtered_records[filtered_records["jurisdiction"].isin(sel_jur)]
if sel_risk and "risk" in filtered_records:
    filtered_records = filtered_records[filtered_records["risk"].isin(sel_risk)]
if sel_mod and "module" in filtered_records:
    filtered_records = filtered_records[filtered_records["module"].isin(sel_mod)]

filtered_families = families.copy()
if sel_jur and "jurisdictions" in filtered_families:
    filtered_families = filtered_families[
        filtered_families["jurisdictions"].fillna("").apply(lambda s: any(j in str(s) for j in sel_jur))
    ]
if sel_risk and "risk" in filtered_families:
    filtered_families = filtered_families[filtered_families["risk"].isin(sel_risk)]
if sel_mod and "module" in filtered_families:
    filtered_families = filtered_families[filtered_families["module"].isin(sel_mod)]

filtered_jur = jurisdictions.copy()
if sel_jur and "jurisdiction" in filtered_jur:
    filtered_jur = filtered_jur[filtered_jur["jurisdiction"].isin(sel_jur)]

filtered_claims = claims.copy()
if sel_jur and "jurisdiction" in filtered_claims:
    filtered_claims = filtered_claims[filtered_claims["jurisdiction"].isin(sel_jur)]

if page == "01 Resumen ejecutivo":
    st.markdown('<div class="section-title">Cockpit ejecutivo</div>', unsafe_allow_html=True)
    st.markdown('<div class="subnote">Lectura rápida para directorio, cliente o comité. Esta vista se alimenta únicamente de tablas normalizadas.</div>', unsafe_allow_html=True)

    total_families = int(filtered_families["family"].nunique()) if not filtered_families.empty and "family" in filtered_families else 0
    total_jur = int(filtered_jur["jurisdiction"].nunique()) if not filtered_jur.empty and "jurisdiction" in filtered_jur else 0
    high_fam = int((filtered_families["risk"] == "Alto").sum()) if not filtered_families.empty and "risk" in filtered_families else 0
    medium_fam = int((filtered_families["risk"] == "Medio").sum()) if not filtered_families.empty and "risk" in filtered_families else 0
    active_mentions = int((filtered_records["status_bucket"] == "Activo / concedido").sum()) if not filtered_records.empty and "status_bucket" in filtered_records else 0
    rec = recommendation_from_data(filtered_records)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("Familias visibles", f"{total_families}", "Universo limpio en la vista", "purple")
    with c2: kpi_card("Jurisdicciones", f"{total_jur}", "Cobertura territorial en filtros")
    with c3: kpi_card("Riesgo alto", f"{high_fam}", "Familias con alerta roja", "pink")
    with c4: kpi_card("Riesgo medio", f"{medium_fam}", "Requieren control activo")
    with c5: kpi_card("Señales activas", f"{active_mentions}", "Menciones activas o concedidas", "green")

    left, right = st.columns([1.5, 1])
    with left:
        st.markdown('<div class="section-title">Mapa ejecutivo de riesgo por jurisdicción</div>', unsafe_allow_html=True)
        fig = px.bar(
            filtered_jur.head(15),
            x="jurisdiction",
            y="riesgo_promedio",
            color="semaforo",
            color_discrete_map={"Alto": PINK, "Medio": CYAN, "Bajo": NOVA_PURPLE, "No definido": GRAY},
            text="familias",
        )
        fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown(
            f'''
            <div class="decision-box">
                <h3>Recomendación ejecutiva automática</h3>
                <p>{rec}</p>
                <div style="margin-top:0.3rem;">
                    <span class="risk-pill risk-red">Rojo = bloqueo o revisión legal inmediata</span>
                    <span class="risk-pill risk-yellow">Ámbar = diseño-around / monitoreo</span>
                    <span class="risk-pill risk-green">Verde = riesgo relativo más bajo</span>
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Top familias visibles</div>', unsafe_allow_html=True)
        st.dataframe(filtered_families.head(8)[["family", "risk", "module", "assignee", "action"]], use_container_width=True, hide_index=True)

elif page == "02 Riesgo FTO por jurisdicción":
    st.markdown('<div class="section-title">Semáforo FTO final por país / jurisdicción</div>', unsafe_allow_html=True)
    st.markdown('<div class="subnote">Vista territorial estable, construida desde la capa normalizada.</div>', unsafe_allow_html=True)

    t1, t2 = st.tabs(["Vista ejecutiva", "Tabla de decisión"])
    with t1:
        c1, c2 = st.columns([1.3, 1])
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Rojo", x=filtered_jur["jurisdiction"], y=filtered_jur["rojos"], marker_color=PINK))
            fig.add_trace(go.Bar(name="Ámbar", x=filtered_jur["jurisdiction"], y=filtered_jur["ambar"], marker_color=CYAN))
            fig.add_trace(go.Bar(name="Verde", x=filtered_jur["jurisdiction"], y=filtered_jur["verdes"], marker_color=NOVA_PURPLE))
            fig.update_layout(barmode="stack", height=430, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown(
                '''
                <div class="info-box">
                    <strong>Cómo leer la matriz territorial.</strong><br><br>
                    Un país puede tener pocas menciones y aun así exigir atención prioritaria si su riesgo máximo es alto o si concentra familias activas con claims críticos.
                </div>
                ''',
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.dataframe(filtered_jur[["jurisdiction", "familias", "riesgo_promedio", "activos", "semaforo"]], use_container_width=True, hide_index=True)
    with t2:
        table = filtered_jur.copy()
        table["recomendacion"] = table["semaforo"].map({
            "Alto": "Revisión legal externa + diseño-around",
            "Medio": "Monitoreo activo + validación técnica",
            "Bajo": "Seguimiento periódico",
            "No definido": "Completar verificación",
        })
        st.dataframe(table[["jurisdiction", "familias", "activos", "semaforo", "recomendacion"]], use_container_width=True, hide_index=True)

elif page == "03 Familias activas y ranking":
    st.markdown('<div class="section-title">Ranking final de familias activas</div>', unsafe_allow_html=True)
    st.markdown('<div class="subnote">Vista orientada a priorizar seguimiento, monitoreo y diseño-around.</div>', unsafe_allow_html=True)

    fam = filtered_families.copy()
    query = st.text_input("Buscar por familia, titular o módulo")
    if query:
        mask = (
            fam["family"].str.contains(query, case=False, na=False)
            | fam["assignee"].str.contains(query, case=False, na=False)
            | fam["module"].str.contains(query, case=False, na=False)
        )
        fam = fam[mask]

    c1, c2 = st.columns([1.25, 1])
    with c1:
        topn = fam.head(15)
        fig = px.bar(topn, x="risk_num", y="family", orientation="h", color="risk",
                     color_discrete_map={"Alto": PINK, "Medio": CYAN, "Bajo": NOVA_PURPLE, "No definido": GRAY},
                     hover_data=["assignee", "module", "status", "action"])
        fig.update_layout(height=520, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        holder = fam.groupby("assignee").agg(familias=("family", "size"), riesgo=("risk_num", "mean")).reset_index()
        holder = holder.sort_values("familias", ascending=False).head(12)
        fig2 = px.treemap(holder, path=["assignee"], values="familias", color="riesgo", color_continuous_scale=[NOVA_PURPLE, CYAN, PINK])
        fig2.update_layout(height=520, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Tabla ejecutiva de seguimiento</div>', unsafe_allow_html=True)
    st.dataframe(fam[["family", "risk", "assignee", "module", "status", "action", "jurisdictions", "sources"]], use_container_width=True, hide_index=True)

elif page == "04 Claim charts y trazabilidad":
    st.markdown('<div class="section-title">Claim charts, coincidencias y trazabilidad</div>', unsafe_allow_html=True)
    st.markdown('<div class="subnote">Panel de drill-down para revisar familias sensibles y la base documental de respaldo.</div>', unsafe_allow_html=True)

    families_opts = sorted([x for x in filtered_claims["family"].dropna().unique().tolist() if str(x).strip()])
    selected_family = st.selectbox("Seleccionar familia", families_opts)
    sub = filtered_claims[filtered_claims["family"] == selected_family].copy()

    c1, c2 = st.columns([1.35, 1])
    with c1:
        show_cols = [c for c in ["jurisdiction", "claim_text", "risk", "status_bucket", "action", "source_file", "source_sheet"] if c in sub.columns]
        st.dataframe(sub[show_cols], use_container_width=True, hide_index=True)
    with c2:
        meta = filtered_families[filtered_families["family"] == selected_family]
        if not meta.empty:
            row = meta.iloc[0]
            st.markdown(
                f'''
                <div class="decision-box">
                    <h3>Ficha rápida de la familia</h3>
                    <p><strong>Riesgo:</strong> {row['risk']}</p>
                    <p><strong>Titular:</strong> {row['assignee']}</p>
                    <p><strong>Módulo:</strong> {row['module']}</p>
                    <p><strong>Estatus:</strong> {row['status']}</p>
                    <p><strong>Acción:</strong> {row['action']}</p>
                </div>
                ''',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-title">Trazabilidad de fuentes</div>', unsafe_allow_html=True)
    st.dataframe(sub[["source_file", "source_sheet", "jurisdiction", "status_bucket"]].drop_duplicates(), use_container_width=True, hide_index=True)

elif page == "05 Patentabilidad preliminar":
    st.markdown('<div class="section-title">Patentabilidad preliminar</div>', unsafe_allow_html=True)
    st.markdown('<div class="subnote">Módulo vivo basado en tabla normalizada. Si no existe, la app sigue funcionando y te indica qué falta.</div>', unsafe_allow_html=True)

    if patentability.empty:
        st.info("Aún no existe `novandino_patentability.csv`. Cuando exportes la base de patentabilidad, este módulo se activará automáticamente.")
    else:
        st.dataframe(patentability, use_container_width=True, hide_index=True)
        if {"categoria", "cantidad"}.issubset(set(patentability.columns)):
            fig = px.bar(patentability, x="categoria", y="cantidad", color="categoria",
                         color_discrete_sequence=[NOVA_PURPLE, CYAN, PINK, YELLOW, GREEN])
            fig.update_layout(height=360, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

elif page == "06 Hoja de ruta":
    st.markdown('<div class="section-title">Hoja de ruta de implementación</div>', unsafe_allow_html=True)
    st.markdown('<div class="subnote">Módulo vivo basado en tabla normalizada de acciones, responsables, plazos y estados.</div>', unsafe_allow_html=True)

    if roadmap.empty:
        st.info("Aún no existe `novandino_roadmap.csv`. Cuando exportes la hoja de ruta en formato estructurado, este módulo se activará automáticamente.")
    else:
        st.dataframe(roadmap, use_container_width=True, hide_index=True)
        if {"responsable", "acciones"}.issubset(set(roadmap.columns)):
            by_owner = roadmap.groupby("responsable").agg(acciones=("acciones", "sum")).reset_index()
            fig = px.bar(by_owner, x="responsable", y="acciones", color="responsable",
                         color_discrete_sequence=[NOVA_PURPLE, CYAN, PINK, YELLOW, GREEN])
            fig.update_layout(height=360, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

elif page == "07 Salud de datos":
    st.markdown('<div class="section-title">Control de carga y salud del modelo de datos</div>', unsafe_allow_html=True)
    st.dataframe(sources, use_container_width=True, hide_index=True)
    completeness = pd.DataFrame([
        {"Campo": "Familia", "Completitud %": round((records["family"] != "").mean() * 100, 1)},
        {"Campo": "Jurisdicción", "Completitud %": round((records["jurisdiction"] != "").mean() * 100, 1)},
        {"Campo": "Riesgo", "Completitud %": round((records["risk"] != "No definido").mean() * 100, 1)},
        {"Campo": "Estatus", "Completitud %": round((records["status_bucket"] != "No definido").mean() * 100, 1)},
        {"Campo": "Acción", "Completitud %": round((records["action"] != "No definida").mean() * 100, 1)},
    ])
    fig = px.bar(completeness, x="Completitud %", y="Campo", orientation="h", color="Completitud %",
                 color_continuous_scale=[PINK, CYAN, NOVA_PURPLE])
    fig.update_layout(height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="footer-note">Versión v2.3. Esta app lee solo capa normalizada e incorpora módulos opcionales de patentabilidad y hoja de ruta.</div>', unsafe_allow_html=True)
