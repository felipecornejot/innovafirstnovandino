
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "normalized_data"
OUT_DIR.mkdir(exist_ok=True)

INPUTS = {
    "matriz_patentes": "Innovafirst_Matriz_Maestra_Patentes_Consolidada_Fase2.xlsx",
    "screening_amplio": "Innovafirst_Screening_Amplio_Exhaustivo_Razonable_Fase2.xlsx",
    "dashboard_fto": "Innovafirst_Dashboard_FTO_Consolidado_Multijurisdiccion.xlsx",
    "claimchart_core": "Innovafirst_ClaimChart_Profundo_Albemarle_US11219863.xlsx",
    "claimchart_tier1b": "Innovafirst_ClaimChart_Profundo_Tier1_Complemento.xlsx",
}

OPTIONAL_INPUTS = {
    "roadmap": "Innovafirst_Hoja_de_Ruta_Implementacion.xlsx",
    "patentability": "Innovafirst_Informe_Preliminar_Patentabilidad.xlsx",
}

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

def score_sheet_relevance(sheet_name: str, df: pd.DataFrame) -> int:
    name = sheet_name.lower()
    score = 0
    positive_terms = ["matriz", "master", "consolidada", "screening", "shortlist", "dashboard", "claim", "chart", "status", "tier", "risk", "famil", "jurisdiction"]
    negative_terms = ["leeme", "readme", "roadmap", "fuentes", "fuente", "metodo", "metodologia", "criterios", "resumen", "control", "notas", "pendientes", "acciones"]
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
    blacklist_starts = ["base utilizada", "criterio rector", "hojas del workbook", "objetivo", "resultado", "estado", "id", "fuentes", "metodologia", "metodología", "version", "versión", "nan", "no definido"]
    if any(joined.startswith(x) for x in blacklist_starts):
        return False
    useful = any(v and v.lower() not in ["nan", "no definido", "n/a", "none"] for v in values)
    return useful

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
    keep_mask = out.apply(lambda r: is_meaningful_record(r, family, country, risk, status, assignee, claim), axis=1)
    out = out[keep_mask].copy()
    if out.empty:
        return pd.DataFrame()

    out["family"] = out[family].astype(str).str.strip() if family else ""
    out["jurisdiction"] = out[country].astype(str).str.strip() if country else ""
    out["risk"] = out[risk].map(normalize_risk) if risk else "No definido"
    out["risk_num"] = pd.to_numeric(out[score], errors="coerce") if score else None
    if "risk_num" not in out or out["risk_num"].isna().all():
        out["risk_num"] = out["risk"].map(risk_num)
    else:
        out["risk_num"] = out["risk_num"].fillna(out["risk"].map(risk_num))
    out["module"] = out[module].astype(str).str.strip() if module else "No definido"
    out["status"] = out[status].astype(str).str.strip() if status else "No definido"
    out["status_bucket"] = out["status"].map(status_bucket)
    out["action"] = out[action].astype(str).str.strip() if action else "No definida"
    out["assignee"] = out[assignee].astype(str).str.strip() if assignee else "No definido"
    out["claim_text"] = out[claim].astype(str).str.strip() if claim else ""
    out["source_file"] = source_file
    out["source_sheet"] = sheet

    cols = ["family", "jurisdiction", "risk", "risk_num", "module", "status", "status_bucket", "action", "assignee", "claim_text", "source_file", "source_sheet"]
    out = out[cols].copy()
    out = out[
        ~out["family"].str.lower().isin(["nan", "no definido", ""])
        | out["claim_text"].ne("")
    ].copy()
    return out

frames = []
source_rows = []

for _, fname in INPUTS.items():
    path = DATA_DIR / fname
    book = read_book(path)
    useful_rows = 0
    for sheet, df in book.items():
        e = enrich(df, fname, sheet)
        if not e.empty:
            useful_rows += len(e)
            frames.append(e)
    source_rows.append({
        "source_file": fname,
        "available": path.exists(),
        "sheets_loaded": len(book),
        "useful_rows": useful_rows,
    })

records = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=[
    "family", "jurisdiction", "risk", "risk_num", "module", "status", "status_bucket", "action", "assignee", "claim_text", "source_file", "source_sheet"
])
records = records.drop_duplicates().copy()

family_summary = (
    records.groupby("family")
    .agg(
        risk_num=("risk_num", "max"),
        assignee=("assignee", lambda s: next((x for x in s if x and x not in ["No definido", "nan"]), "No definido")),
        module=("module", lambda s: next((x for x in s if x and x not in ["No definido", "nan"]), "No definido")),
        status=("status_bucket", lambda s: next((x for x in s if x and x != "No definido"), "No definido")),
        action=("action", lambda s: next((x for x in s if x and x not in ["No definida", "nan"]), "No definida")),
        jurisdictions=("jurisdiction", lambda s: ", ".join(sorted({x for x in s if x and x.lower() not in ['nan', 'no definido']}))),
        rows=("family", "size"),
        sources=("source_file", lambda s: ", ".join(sorted(set(s)))),
    )
    .reset_index()
)
family_summary["risk"] = family_summary["risk_num"].map({3: "Alto", 2: "Medio", 1: "Bajo", 0: "No definido"})

jurisdiction_summary = (
    records[records["jurisdiction"].str.lower().ne("nan") & records["jurisdiction"].ne("")]
    .groupby("jurisdiction")
    .agg(
        total=("jurisdiction", "size"),
        familias=("family", lambda s: len({x for x in s if x and x.lower() not in ['nan', 'no definido']})),
        riesgo_promedio=("risk_num", "mean"),
        riesgo_max=("risk_num", "max"),
        rojos=("risk", lambda s: int((s == "Alto").sum())),
        ambar=("risk", lambda s: int((s == "Medio").sum())),
        verdes=("risk", lambda s: int((s == "Bajo").sum())),
        activos=("status_bucket", lambda s: int((s == "Activo / concedido").sum())),
    )
    .reset_index()
)
jurisdiction_summary["semaforo"] = jurisdiction_summary["riesgo_max"].map({3: "Alto", 2: "Medio", 1: "Bajo", 0: "No definido"})

claims = records[records["claim_text"] != ""].copy()
source_control = pd.DataFrame(source_rows)

records.to_csv(OUT_DIR / "novandino_records.csv", index=False)
family_summary.to_csv(OUT_DIR / "novandino_family_summary.csv", index=False)
jurisdiction_summary.to_csv(OUT_DIR / "novandino_jurisdiction_summary.csv", index=False)
claims.to_csv(OUT_DIR / "novandino_claims.csv", index=False)
source_control.to_csv(OUT_DIR / "novandino_source_control.csv", index=False)

roadmap_file = DATA_DIR / OPTIONAL_INPUTS["roadmap"]
if roadmap_file.exists():
    try:
        xls = pd.ExcelFile(roadmap_file)
        df = pd.read_excel(roadmap_file, sheet_name=xls.sheet_names[0])
        df.columns = [snake(str(c)) for c in df.columns]
        action_col = pick_col(df, ["actividad", "accion", "acción", "action", "tarea"])
        owner_col = pick_col(df, ["responsable", "owner", "encargado"])
        prio_col = pick_col(df, ["prioridad", "priority"])
        due_col = pick_col(df, ["fecha", "plazo", "deadline", "due"])
        status_col = pick_col(df, ["estado", "status"])
        road = pd.DataFrame({
            "accion": df[action_col].astype(str) if action_col else "",
            "responsable": df[owner_col].astype(str) if owner_col else "",
            "prioridad": df[prio_col].astype(str) if prio_col else "",
            "plazo": df[due_col].astype(str) if due_col else "",
            "estado": df[status_col].astype(str) if status_col else "",
        })
        road = road[road["accion"].str.strip() != ""].copy()
        road["acciones"] = 1
        road.to_csv(OUT_DIR / "novandino_roadmap.csv", index=False)
    except Exception:
        pass

pat_file = DATA_DIR / OPTIONAL_INPUTS["patentability"]
if pat_file.exists():
    try:
        xls = pd.ExcelFile(pat_file)
        df = pd.read_excel(pat_file, sheet_name=xls.sheet_names[0])
        df.columns = [snake(str(c)) for c in df.columns]
        category_col = pick_col(df, ["categoria", "category", "dimension", "tema"])
        value_col = pick_col(df, ["cantidad", "count", "valor", "score", "puntaje"])
        if category_col and value_col:
            pat = pd.DataFrame({
                "categoria": df[category_col].astype(str),
                "cantidad": pd.to_numeric(df[value_col], errors="coerce").fillna(0),
            })
        else:
            first_text = df.columns[0] if len(df.columns) else None
            if first_text:
                value_counts = df[first_text].astype(str).value_counts().reset_index()
                value_counts.columns = ["categoria", "cantidad"]
                pat = value_counts
            else:
                pat = pd.DataFrame(columns=["categoria", "cantidad"])
        pat = pat[pat["categoria"].str.strip() != ""].copy()
        pat.to_csv(OUT_DIR / "novandino_patentability.csv", index=False)
    except Exception:
        pass

print("Normalized layer v2 built in:", OUT_DIR)
for fname in sorted([p.name for p in OUT_DIR.glob("*.csv")]):
    print("-", fname)
