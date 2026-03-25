
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Novandino | Executive IP Dashboard v2.1",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#333A47"
CYAN = "#31C1D4"
SOFT = "#F0F0F0"
PINK = "#FFB8D1"
GRAY = "#6D6D6E"
WHITE = "#FFFFFF"
NOVA_PURPLE = "#4F2ACB"
NOVA_PURPLE_DARK = "#3C1DAA"
NOVA_PURPLE_SOFT = "#EDE8FF"
RED = "#E16060"
YELLOW = "#D8A22B"
GREEN = "#3B9B6B"
BG = "#F7F8FB"

DATA_DIR = Path(__file__).parent / "data"
ASSETS_DIR = Path(__file__).parent / "assets"

REQUIRED_FILES = {
    "matriz_patentes": "Innovafirst_Matriz_Maestra_Patentes_Consolidada_Fase2.xlsx",
    "screening_amplio": "Innovafirst_Screening_Amplio_Exhaustivo_Razonable_Fase2.xlsx",
    "dashboard_fto": "Innovafirst_Dashboard_FTO_Consolidado_Multijurisdiccion.xlsx",
    "claimchart_core": "Innovafirst_ClaimChart_Profundo_Albemarle_US11219863.xlsx",
    "claimchart_tier1b": "Innovafirst_ClaimChart_Profundo_Tier1_Complemento.xlsx",
}

OPTIONAL_FILES = {
    "logo_novandino": "novandino_logo.png",
}

# =========================================================
# STYLE
# =========================================================
st.markdown(
    f"""
    <style>
        .stApp {{
            background:
                radial-gradient(circle at top right, rgba(79,42,203,0.08), transparent 18%),
                radial-gradient(circle at left top, rgba(49,193,212,0.10), transparent 20%),
                linear-gradient(180deg, #fafbfe 0%, #f4f7fb 100%);
        }}
        .main .block-container {{
            max-width: 1500px;
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(51,58,71,0.98), rgba(60,29,170,0.98));
        }}
        section[data-testid="stSidebar"] * {{
            color: white !important;
        }}
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stMultiSelect label,
        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {{
            color: white !important;
        }}
        section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
        section[data-testid="stSidebar"] div[data-baseweb="select"] span {{
            color: white !important;
            background-color: rgba(255,255,255,0.06) !important;
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label p {{
            color: white !important;
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
    """,
    unsafe_allow_html=True,
)

# =========================================================
# HELPERS
# =========================================================
def normalize_text(v: object) -> str:
    if pd.isna(v):
        return ""
    return str(v).strip()


def snake(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9áéíóúÁÉÍÓÚñÑ]+", "_", text.strip().lower())
    return re.sub(r"_+", "_", text).strip("_")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [snake(str(c)) for c in out.columns]
    return out


def pick_col(df: pd.DataFrame, keys: List[str]) -> Optional[str]:
    for k in keys:
        for c in df.columns:
            if k in c:
                return c
    return None


def normalize_risk(v: object) -> str:
    t = normalize_text(v).lower()
    if not t:
        return "No definido"
    if any(x in t for x in ["alto", "high", "critical", "critico", "crítico", "rojo", "red"]):
        return "Alto"
    if any(x in t for x in ["medio", "medium", "amber", "yellow", "amarillo", "moderado"]):
        return "Medio"
    if any(x in t for x in ["bajo", "low", "green", "verde"]):
        return "Bajo"
    if any(x in t for x in ["monitor", "watch", "seguimiento"]):
        return "Monitor"
    return "No definido"


def risk_num(v: object) -> int:
    return {"Alto": 3, "Medio": 2, "Bajo": 1, "Monitor": 1, "No definido": 0}.get(normalize_risk(v), 0)


def status_bucket(v: object) -> str:
    t = normalize_text(v).lower()
    if not t:
        return "No definido"
    if any(x in t for x in ["active", "vigente", "granted", "grant", "issued"]):
        return "Activo / concedido"
    if any(x in t for x in ["pending", "solicitud", "en tramite", "en trámite"]):
        return "Pending / en trámite"
    if any(x in t for x in ["expired", "ceased", "withdrawn", "abandoned", "lapsed", "terminated"]):
        return "No activo"
    if "verify" in t or "pendiente" in t:
        return "Verificar"
    return "No definido"


def recommendation_from_data(df: pd.DataFrame) -> str:
    if df.empty:
        return "Cargar los archivos estructurados para habilitar recomendaciones ejecutivas."
    high = int((df["_risk"] == "Alto").sum())
    medium = int((df["_risk"] == "Medio").sum())
    active = int((df["_status_bucket"] == "Activo / concedido").sum())
    if high >= 8:
        return "Priorizar revisión legal externa y diseño-around en familias críticas antes de cualquier decisión territorial o de filing adicional."
    if high >= 3:
        return "Mantener control activo sobre familias rojas, cerrar validación de estatus y modular decisiones país por país."
    if medium >= 10 and active >= 5:
        return "El universo requiere monitoreo intensivo, pero aún parece gestionable si se estructura un plan de seguimiento y cierre técnico."
    return "La base actual sugiere un escenario controlable; conviene endurecer patentabilidad y hoja de ruta antes de mover la estrategia de protección."


def score_sheet_relevance(sheet_name: str, df: pd.DataFrame) -> int:
    name = sheet_name.lower()
    score = 0
    positive_terms = [
        "matriz", "master", "consolidada", "screening", "shortlist", "dashboard",
        "claim", "chart", "status", "tier", "risk", "famil", "jurisdiction"
    ]
    negative_terms = [
        "leeme", "readme", "roadmap", "fuentes", "fuente", "metodo", "metodologia",
        "criterios", "resumen", "control", "notas", "pendientes", "acciones"
    ]
    for t in positive_terms:
        if t in name:
            score += 2
    for t in negative_terms:
        if t in name:
            score -= 3

    cols = [str(c).lower() for c in df.columns]
    for c in cols:
        if any(k in c for k in ["famil", "family", "jurisdiction", "riesgo", "risk", "status", "claim", "titular", "module"]):
            score += 1

    # penaliza hojas sin filas o demasiado chicas
    if df.shape[0] < 3:
        score -= 2
    return score


def is_meaningful_record(row: pd.Series, family: str, jurisdiction: str, risk: str, status: str, assignee: str, claim: str) -> bool:
    values = [
        normalize_text(row.get(family, "")) if family else "",
        normalize_text(row.get(jurisdiction, "")) if jurisdiction else "",
        normalize_text(row.get(risk, "")) if risk else "",
        normalize_text(row.get(status, "")) if status else "",
        normalize_text(row.get(assignee, "")) if assignee else "",
        normalize_text(row.get(claim, "")) if claim else "",
    ]
    joined = " | ".join([v.lower() for v in values if v]).strip()
    if not joined:
        return False

    blacklist_starts = [
        "base utilizada", "criterio rector", "hojas del workbook", "objetivo", "resultado",
        "estado", "id", "fuentes", "metodologia", "metodología", "version", "versión",
        "nan", "no definido"
    ]
    if any(joined.startswith(x) for x in blacklist_starts):
        return False

    # al menos un elemento útil
    useful = any(v and v.lower() not in ["nan", "no definido", "n/a", "none"] for v in values)
    return useful


@st.cache_data(show_spinner=False)
def read_book(path: Path) -> Dict[str, pd.DataFrame]:
    if not path.exists():
        return {}
    xls = pd.ExcelFile(path)
    out = {}
    for sheet in xls.sheet_names:
        raw = pd.read_excel(path, sheet_name=sheet)
        if raw is None or raw.empty:
            continue
        df = normalize_columns(raw)
        if score_sheet_relevance(sheet, df) <= 0:
            continue
        out[sheet] = df
    return out


@st.cache_data(show_spinner=False)
def load_books() -> Dict[str, Dict[str, pd.DataFrame]]:
    return {key: read_book(DATA_DIR / fname) for key, fname in REQUIRED_FILES.items()}


def enrich(df: pd.DataFrame, source_file: str, sheet: str) -> pd.DataFrame:
    family = pick_col(df, ["family", "familia"])
    country = pick_col(df, ["jurisdiction", "country", "pais", "país", "territory"])
    risk = pick_col(df, ["risk", "riesgo", "semaforo", "semáforo"])
    score = pick_col(df, ["score", "puntaje", "ranking", "priority"])
    module = pick_col(df, ["module", "modulo", "módulo", "cluster"])
    status = pick_col(df, ["status", "estado", "legal_status"])
    action = pick_col(df, ["action", "recomend", "recommendation", "accion", "acción"])
    assignee = pick_col(df, ["assignee", "titular", "owner", "applicant", "company"])
    claim = pick_col(df, ["claim", "reivindic"])

    out = df.copy()

    # filtra filas narrativas/metadata
    keep_mask = out.apply(lambda r: is_meaningful_record(r, family, country, risk, status, assignee, claim), axis=1)
    out = out[keep_mask].copy()
    if out.empty:
        return pd.DataFrame()

    out["_source_file"] = source_file
    out["_sheet"] = sheet
    out["_family"] = out[family].astype(str).str.strip() if family else ""
    out["_jurisdiction"] = out[country].astype(str).str.strip() if country else ""
    out["_risk_raw"] = out[risk] if risk else ""
    out["_risk"] = out["_risk_raw"].map(normalize_risk)
    out["_risk_num"] = pd.to_numeric(out[score], errors="coerce") if score else None
    if "_risk_num" not in out or out["_risk_num"].isna().all():
        out["_risk_num"] = out["_risk"].map(risk_num)
    else:
        out["_risk_num"] = out["_risk_num"].fillna(out["_risk"].map(risk_num))

    out["_module"] = out[module].astype(str).str.strip() if module else "No definido"
    out["_status"] = out[status].astype(str).str.strip() if status else "No definido"
    out["_status_bucket"] = out["_status"].map(status_bucket)
    out["_action"] = out[action].astype(str).str.strip() if action else "No definida"
    out["_assignee"] = out[assignee].astype(str).str.strip() if assignee else "No definido"
    out["_claim"] = out[claim].astype(str).str.strip() if claim else ""
    return out


@st.cache_data(show_spinner=False)
def build_master() -> pd.DataFrame:
    books = load_books()
    frames = []
    for key, book in books.items():
        fname = REQUIRED_FILES[key]
        for sheet, df in book.items():
            e = enrich(df, fname, sheet)
            if e is not None and not e.empty:
                frames.append(e)
    if not frames:
        return pd.DataFrame()
    master = pd.concat(frames, ignore_index=True, sort=False)

    # limpieza final
    for c in ["_family", "_jurisdiction", "_module", "_status", "_action", "_assignee", "_claim"]:
        master[c] = master[c].fillna("").astype(str).str.strip()

    # elimina registros inútiles
    bad_family = master["_family"].str.lower().isin(["nan", "no definido", ""])
    bad_claim_only = master["_claim"].eq("") & bad_family
    master = master[~bad_claim_only].copy()

    return master


def build_family_summary(master: pd.DataFrame) -> pd.DataFrame:
    fam = master[master["_family"] != ""].copy()
    if fam.empty:
        return pd.DataFrame()
    out = (
        fam.groupby("_family")
        .agg(
            risk_num=("_risk_num", "max"),
            assignee=("_assignee", lambda s: next((x for x in s if x and x not in ["No definido", "nan"]), "No definido")),
            module=("_module", lambda s: next((x for x in s if x and x not in ["No definido", "nan"]), "No definido")),
            status=("_status_bucket", lambda s: next((x for x in s if x and x != "No definido"), "No definido")),
            action=("_action", lambda s: next((x for x in s if x and x not in ["No definida", "nan"]), "No definida")),
            jurisdictions=("_jurisdiction", lambda s: ", ".join(sorted({x for x in s if x and x not in ['nan', 'No definido']}))),
            rows=("_family", "size"),
            sources=("_source_file", lambda s: ", ".join(sorted(set(s)))),
        )
        .reset_index()
    )
    out["risk"] = out["risk_num"].map({3: "Alto", 2: "Medio", 1: "Bajo", 0: "No definido"})
    out = out[~out["_family"].str.lower().isin(["nan", "no definido", ""])]
    return out.sort_values(["risk_num", "rows"], ascending=[False, False])


def build_jurisdiction_summary(master: pd.DataFrame) -> pd.DataFrame:
    j = master[master["_jurisdiction"] != ""].copy()
    j = j[~j["_jurisdiction"].str.lower().isin(["nan", "no definido", "jurisdiccion", "jurisdiction"])]
    if j.empty:
        return pd.DataFrame()
    out = (
        j.groupby("_jurisdiction")
        .agg(
            total=("_jurisdiction", "size"),
            familias=("_family", lambda s: len({x for x in s if x and x.lower() not in ['nan', 'no definido']})),
            riesgo_promedio=("_risk_num", "mean"),
            riesgo_max=("_risk_num", "max"),
            rojos=("_risk", lambda s: int((s == "Alto").sum())),
            ambar=("_risk", lambda s: int((s == "Medio").sum())),
            verdes=("_risk", lambda s: int((s == "Bajo").sum())),
            activos=("_status_bucket", lambda s: int((s == "Activo / concedido").sum())),
        )
        .reset_index()
    )
    out["semaforo"] = out["riesgo_max"].map({3: "Alto", 2: "Medio", 1: "Bajo", 0: "No definido"})
    return out.sort_values(["riesgo_max", "riesgo_promedio", "familias"], ascending=[False, False, False])


def build_claim_summary(master: pd.DataFrame) -> pd.DataFrame:
    c = master[(master["_claim"] != "") | (master["_sheet"].str.contains("claim", case=False, na=False))].copy()
    if c.empty:
        return pd.DataFrame()
    return c


def header():
    logo = ASSETS_DIR / OPTIONAL_FILES["logo_novandino"]
    c1, c2 = st.columns([1, 4])
    with c1:
        if logo.exists():
            st.image(str(logo), use_container_width=True)
    with c2:
        st.markdown(
            """
            <div class="hero">
                <div class="hero-title">Novandino | Executive IP Dashboard v2.1</div>
                <p class="hero-sub">
                    Panel gerencial para libertad de operación, patentabilidad preliminar, vigilancia tecnológica y seguimiento ejecutivo.
                    Diseñado con lógica Innovafirst y acentos visuales armonizados con Novandino.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def kpi_card(label: str, value: str, foot: str = "", cls: str = ""):
    extra = f" {cls}" if cls else ""
    st.markdown(
        f"""
        <div class="metric-card{extra}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_missing_files():
    return [fname for fname in REQUIRED_FILES.values() if not (DATA_DIR / fname).exists()]

# =========================================================
# LOAD
# =========================================================
master = build_master()
family_summary = build_family_summary(master)
jurisdiction_summary = build_jurisdiction_summary(master)
claim_summary = build_claim_summary(master)
missing_files = get_missing_files()

header()

if master.empty:
    st.error("No se detectaron registros útiles en los Excel cargados. Revisa nombres de columnas, hojas y contenido estructurado.")
    st.stop()

if missing_files:
    st.warning("Faltan archivos esperados. La app sigue funcionando con lo disponible, pero el panorama quedará incompleto.")
    for mf in missing_files:
        st.write(f"- {mf}")

# sidebar
st.sidebar.markdown("## Navegación")
page = st.sidebar.radio(
    "Ir a",
    [
        "01 Resumen ejecutivo",
        "02 Riesgo FTO por jurisdicción",
        "03 Familias activas y ranking",
        "04 Claim charts y trazabilidad",
        "05 Salud de datos",
    ],
)

st.sidebar.markdown("## Filtros")
jur_options = sorted([x for x in master["_jurisdiction"].dropna().unique() if x and x.lower() not in ["nan", "no definido"]])
risk_options = sorted([x for x in master["_risk"].dropna().unique() if x and x != "No definido"])
module_options = sorted([x for x in master["_module"].dropna().unique() if x and x.lower() not in ["nan", "no definido"]])

sel_jur = st.sidebar.multiselect("Jurisdicción", jur_options)
sel_risk = st.sidebar.multiselect("Riesgo", risk_options, default=risk_options)
sel_mod = st.sidebar.multiselect("Módulo", module_options)

filtered = master.copy()
if sel_jur:
    filtered = filtered[filtered["_jurisdiction"].isin(sel_jur)]
if sel_risk:
    filtered = filtered[filtered["_risk"].isin(sel_risk)]
if sel_mod:
    filtered = filtered[filtered["_module"].isin(sel_mod)]

family_filtered = build_family_summary(filtered)
jur_filtered = build_jurisdiction_summary(filtered)
claim_filtered = build_claim_summary(filtered)

# =========================================================
# PAGE 01
# =========================================================
if page == "01 Resumen ejecutivo":
    st.markdown('<div class="section-title">Cockpit ejecutivo</div>', unsafe_allow_html=True)
    st.markdown('<div class="subnote">Lectura rápida para directorio, cliente o comité. Prioriza claridad, semáforo y acción recomendada.</div>', unsafe_allow_html=True)

    total_families = int(family_filtered["_family"].nunique()) if not family_filtered.empty else 0
    total_jur = int(jur_filtered["_jurisdiction"].nunique()) if not jur_filtered.empty else 0
    high_fam = int((family_filtered["risk"] == "Alto").sum()) if not family_filtered.empty else 0
    medium_fam = int((family_filtered["risk"] == "Medio").sum()) if not family_filtered.empty else 0
    active_mentions = int((filtered["_status_bucket"] == "Activo / concedido").sum()) if not filtered.empty else 0
    rec = recommendation_from_data(filtered)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("Familias visibles", f"{total_families}", "Universo cargado en la vista", "purple")
    with c2: kpi_card("Jurisdicciones", f"{total_jur}", "Cobertura territorial en filtros")
    with c3: kpi_card("Riesgo alto", f"{high_fam}", "Familias con alerta roja", "pink")
    with c4: kpi_card("Riesgo medio", f"{medium_fam}", "Requieren control activo")
    with c5: kpi_card("Señales activas", f"{active_mentions}", "Menciones activas o concedidas", "green")

    left, right = st.columns([1.5, 1])
    with left:
        st.markdown('<div class="section-title">Mapa ejecutivo de riesgo por jurisdicción</div>', unsafe_allow_html=True)
        if not jur_filtered.empty:
            chart = jur_filtered.head(15).copy()
            fig = px.bar(
                chart,
                x="_jurisdiction",
                y="riesgo_promedio",
                color="semaforo",
                color_discrete_map={"Alto": PINK, "Medio": CYAN, "Bajo": NOVA_PURPLE, "No definido": GRAY},
                text="familias",
            )
            fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos suficientes por jurisdicción en la selección actual.")
    with right:
        st.markdown(
            f"""
            <div class="decision-box">
                <h3>Recomendación ejecutiva automática</h3>
                <p>{rec}</p>
                <div style="margin-top:0.3rem;">
                    <span class="risk-pill risk-red">Rojo = bloqueo o revisión legal inmediata</span>
                    <span class="risk-pill risk-yellow">Ámbar = diseño-around / monitoreo</span>
                    <span class="risk-pill risk-green">Verde = riesgo relativo más bajo</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Top familias visibles</div>', unsafe_allow_html=True)
        st.dataframe(family_filtered.head(8)[["_family", "risk", "module", "assignee", "action"]], use_container_width=True, hide_index=True)

    b1, b2 = st.columns([1, 1])
    with b1:
        st.markdown('<div class="section-title">Distribución del riesgo</div>', unsafe_allow_html=True)
        if not family_filtered.empty:
            risk_counts = family_filtered["risk"].value_counts().reset_index()
            risk_counts.columns = ["Riesgo", "Cantidad"]
            fig2 = px.pie(risk_counts, names="Riesgo", values="Cantidad", hole=0.58,
                          color="Riesgo",
                          color_discrete_map={"Alto": PINK, "Medio": CYAN, "Bajo": NOVA_PURPLE, "No definido": GRAY})
            fig2.update_layout(height=340, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=10, b=10))
            st.plotly_chart(fig2, use_container_width=True)
    with b2:
        st.markdown('<div class="section-title">Módulos con mayor carga</div>', unsafe_allow_html=True)
        mod = (
            filtered[filtered["_module"].str.lower().ne("no definido") & filtered["_module"].ne("")]
            .groupby("_module")
            .agg(registros=("_module", "size"), riesgo=("_risk_num", "mean"))
            .reset_index()
            .sort_values("registros", ascending=False)
            .head(10)
        )
        if not mod.empty:
            fig3 = px.bar(mod, x="registros", y="_module", orientation="h", color="riesgo",
                          color_continuous_scale=[NOVA_PURPLE, CYAN, PINK])
            fig3.update_layout(height=340, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig3, use_container_width=True)

# =========================================================
# PAGE 02
# =========================================================
elif page == "02 Riesgo FTO por jurisdicción":
    st.markdown('<div class="section-title">Semáforo FTO final por país / jurisdicción</div>', unsafe_allow_html=True)
    st.markdown('<div class="subnote">Esta vista resume temperatura, actividad y prioridad de seguimiento territorial.</div>', unsafe_allow_html=True)

    if jur_filtered.empty:
        st.info("No hay datos suficientes por jurisdicción en la selección actual.")
    else:
        t1, t2 = st.tabs(["Vista ejecutiva", "Tabla de decisión"])
        with t1:
            c1, c2 = st.columns([1.3, 1])
            with c1:
                fig = go.Figure()
                fig.add_trace(go.Bar(name="Rojo", x=jur_filtered["_jurisdiction"], y=jur_filtered["rojos"], marker_color=PINK))
                fig.add_trace(go.Bar(name="Ámbar", x=jur_filtered["_jurisdiction"], y=jur_filtered["ambar"], marker_color=CYAN))
                fig.add_trace(go.Bar(name="Verde", x=jur_filtered["_jurisdiction"], y=jur_filtered["verdes"], marker_color=NOVA_PURPLE))
                fig.update_layout(barmode="stack", height=430, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.markdown(
                    """
                    <div class="info-box">
                        <strong>Cómo leer la matriz territorial.</strong><br><br>
                        Un país puede tener pocas menciones y aun así exigir atención prioritaria si su riesgo máximo es alto o si concentra familias activas con claims críticos.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                st.dataframe(jur_filtered[["_jurisdiction", "familias", "riesgo_promedio", "activos", "semaforo"]], use_container_width=True, hide_index=True)
        with t2:
            table = jur_filtered.copy()
            table["recomendacion"] = table["semaforo"].map({
                "Alto": "Revisión legal externa + diseño-around",
                "Medio": "Monitoreo activo + validación técnica",
                "Bajo": "Seguimiento periódico",
                "No definido": "Completar verificación",
            })
            st.dataframe(table[["_jurisdiction", "familias", "activos", "semaforo", "recomendacion"]], use_container_width=True, hide_index=True)

        st.markdown('<div class="section-title">Detalle de familias por territorio</div>', unsafe_allow_html=True)
        detail = filtered[(filtered["_family"] != "") & (filtered["_jurisdiction"] != "")]
        detail = detail[["_jurisdiction", "_family", "_risk", "_status_bucket", "_assignee", "_action", "_source_file"]].drop_duplicates()
        st.dataframe(detail, use_container_width=True, hide_index=True)

# =========================================================
# PAGE 03
# =========================================================
elif page == "03 Familias activas y ranking":
    st.markdown('<div class="section-title">Ranking final de familias activas</div>', unsafe_allow_html=True)
    st.markdown('<div class="subnote">Vista orientada a priorizar seguimiento, monitoreo y diseño-around.</div>', unsafe_allow_html=True)

    fam = family_filtered.copy()
    query = st.text_input("Buscar por familia, titular o módulo")
    if query:
        mask = (
            fam["_family"].str.contains(query, case=False, na=False)
            | fam["assignee"].str.contains(query, case=False, na=False)
            | fam["module"].str.contains(query, case=False, na=False)
        )
        fam = fam[mask]

    if fam.empty:
        st.info("No hay familias útiles en la selección actual.")
    else:
        c1, c2 = st.columns([1.25, 1])
        with c1:
            topn = fam.head(15)
            fig = px.bar(
                topn, x="risk_num", y="_family", orientation="h", color="risk",
                color_discrete_map={"Alto": PINK, "Medio": CYAN, "Bajo": NOVA_PURPLE, "No definido": GRAY},
                hover_data=["assignee", "module", "status", "action"],
            )
            fig.update_layout(height=520, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            holder = fam.groupby("assignee").agg(familias=("_family", "size"), riesgo=("risk_num", "mean")).reset_index()
            holder = holder.sort_values("familias", ascending=False).head(12)
            fig2 = px.treemap(holder, path=["assignee"], values="familias", color="riesgo", color_continuous_scale=[NOVA_PURPLE, CYAN, PINK])
            fig2.update_layout(height=520, paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=10, b=10))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-title">Tabla ejecutiva de seguimiento</div>', unsafe_allow_html=True)
        st.dataframe(fam[["_family", "risk", "assignee", "module", "status", "action", "jurisdictions", "sources"]], use_container_width=True, hide_index=True)

# =========================================================
# PAGE 04
# =========================================================
elif page == "04 Claim charts y trazabilidad":
    st.markdown('<div class="section-title">Claim charts, coincidencias y trazabilidad</div>', unsafe_allow_html=True)
    st.markdown('<div class="subnote">Panel de drill-down para revisar familias sensibles y la base documental de respaldo.</div>', unsafe_allow_html=True)

    if claim_filtered.empty:
        st.info("No se detectaron registros de claim chart útiles en los archivos cargados.")
    else:
        families = sorted([x for x in claim_filtered["_family"].dropna().unique() if x and x.lower() not in ["nan", "no definido"]])
        if not families:
            st.info("No hay familias útiles con claim chart en la selección actual.")
        else:
            selected_family = st.selectbox("Seleccionar familia", families)
            sub = claim_filtered[claim_filtered["_family"] == selected_family].copy()

            c1, c2 = st.columns([1.35, 1])
            with c1:
                show_cols = [c for c in ["_jurisdiction", "_claim", "_risk", "_status_bucket", "_action", "_source_file", "_sheet"] if c in sub.columns]
                visible = sub[show_cols + [c for c in sub.columns if not c.startswith("_")][:8]]
                st.dataframe(visible, use_container_width=True, hide_index=True)
            with c2:
                meta = family_summary[family_summary["_family"] == selected_family]
                if not meta.empty:
                    row = meta.iloc[0]
                    st.markdown(
                        f"""
                        <div class="decision-box">
                            <h3>Ficha rápida de la familia</h3>
                            <p><strong>Riesgo:</strong> {row['risk']}</p>
                            <p><strong>Titular:</strong> {row['assignee']}</p>
                            <p><strong>Módulo:</strong> {row['module']}</p>
                            <p><strong>Estatus:</strong> {row['status']}</p>
                            <p><strong>Acción:</strong> {row['action']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown('<div class="section-title">Trazabilidad de fuentes</div>', unsafe_allow_html=True)
            trace = sub[["_source_file", "_sheet", "_jurisdiction", "_status_bucket"]].drop_duplicates()
            st.dataframe(trace, use_container_width=True, hide_index=True)

# =========================================================
# PAGE 05
# =========================================================
elif page == "05 Salud de datos":
    st.markdown('<div class="section-title">Control de carga y salud del modelo de datos</div>', unsafe_allow_html=True)

    rows = []
    books = load_books()
    for key, fname in REQUIRED_FILES.items():
        book = books.get(key, {})
        rows.append({
            "Archivo": fname,
            "Disponible": "Sí" if (DATA_DIR / fname).exists() else "No",
            "Hojas leídas": len(book),
            "Filas útiles": int(sum(df.shape[0] for df in book.values())) if book else 0,
        })
    control = pd.DataFrame(rows)
    st.dataframe(control, use_container_width=True, hide_index=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        completeness = pd.DataFrame([
            {"Campo": "Familia", "Completitud %": round((master["_family"] != "").mean() * 100, 1)},
            {"Campo": "Jurisdicción", "Completitud %": round((master["_jurisdiction"] != "").mean() * 100, 1)},
            {"Campo": "Riesgo", "Completitud %": round((master["_risk"] != "No definido").mean() * 100, 1)},
            {"Campo": "Estatus", "Completitud %": round((master["_status_bucket"] != "No definido").mean() * 100, 1)},
            {"Campo": "Acción", "Completitud %": round((master["_action"] != "No definida").mean() * 100, 1)},
        ])
        fig = px.bar(completeness, x="Completitud %", y="Campo", orientation="h", color="Completitud %",
                     color_continuous_scale=[PINK, CYAN, NOVA_PURPLE])
        fig.update_layout(height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown(
            """
            <div class="info-box">
                <strong>Prioridades de hardening</strong><br><br>
                1. Unificar columnas entre workbooks.<br>
                2. Consolidar IDs únicos por familia.<br>
                3. Exportar shortlist, patentabilidad y hoja de ruta en Excel para integrarlas a esta versión.<br>
                4. Migrar a Parquet o SQLite cuando el modelo esté estable.<br>
                5. Añadir autenticación si la publicación será externa.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">Explorador de datos</div>', unsafe_allow_html=True)
    origins = sorted(set(master["_source_file"].astype(str) + " | " + master["_sheet"].astype(str)))
    selected_origin = st.selectbox("Elegir origen", origins)
    src_file, src_sheet = [x.strip() for x in selected_origin.split("|", 1)]
    sub = master[(master["_source_file"] == src_file) & (master["_sheet"] == src_sheet)]
    st.dataframe(sub, use_container_width=True, hide_index=True)

st.markdown('<div class="footer-note">Versión corregida. El motor ahora ignora hojas narrativas y filas de metadata para poblar correctamente gráficos y tablas ejecutivas.</div>', unsafe_allow_html=True)
