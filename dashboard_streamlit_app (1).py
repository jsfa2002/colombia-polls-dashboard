"""
Colombia 2026 — Dashboard de Encuestas
Basado en el archivo polls_2026.parquet generado por ColombiaScrapp.ipynb

Columnas del dataset: candidate, vote, source, date

Instalar:
    pip install streamlit plotly pandas

Correr:
    streamlit run dashboard_streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────
st.set_page_config(
    page_title="Colombia 2026 | Encuestas",
    page_icon="🇨🇴",
    layout="wide",
)

# Colores por candidato — los mismos que en el notebook
COLORES = {
    "Iván Cepeda":              "#e63946",
    "Abelardo de la Espriella": "#f4a261",
    "Paloma Valencia":          "#2a9d8f",
    "Sergio Fajardo":           "#457b9d",
    "Claudia López":            "#8338ec",
    "Vicky Dávila":             "#fb8500",
    "Voto en blanco":           "#adb5bd",
}


# ─────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────
@st.cache_data
def load_data():
    """
    Intenta cargar polls_2026.parquet (lo que genera save() en el notebook).
    Si no existe, carga el CSV. Si tampoco, usa datos de ejemplo.
    """
    try:
        df = pd.read_parquet("polls_2026.parquet")
        df["date"] = pd.to_datetime(df["date"])
        return df, "parquet"
    except FileNotFoundError:
        pass
    try:
        df = pd.read_csv("polls_2026.csv")
        df["date"] = pd.to_datetime(df["date"])
        return df, "csv"
    except FileNotFoundError:
        pass

    # Datos de ejemplo si no corriste el pipeline todavía
    data = [
        {"date": "2026-03-25", "source": "AtlasIntel", "candidate": "Iván Cepeda",                "vote": 35.7},
        {"date": "2026-03-25", "source": "AtlasIntel", "candidate": "Abelardo de la Espriella",   "vote": 26.8},
        {"date": "2026-03-25", "source": "AtlasIntel", "candidate": "Paloma Valencia",            "vote": 16.8},
        {"date": "2026-03-25", "source": "AtlasIntel", "candidate": "Sergio Fajardo",             "vote": 7.8},
        {"date": "2026-03-25", "source": "AtlasIntel", "candidate": "Claudia López",              "vote": 1.6},
        {"date": "2026-03-25", "source": "AtlasIntel", "candidate": "Voto en blanco",             "vote": 3.9},
        {"date": "2026-03-25", "source": "CNC",        "candidate": "Paloma Valencia",            "vote": 17.5},
        {"date": "2026-03-25", "source": "CNC",        "candidate": "Claudia López",              "vote": 1.7},
        {"date": "2026-03-20", "source": "GAD3",       "candidate": "Paloma Valencia",            "vote": 17.5},
        {"date": "2026-03-20", "source": "GAD3",       "candidate": "Claudia López",              "vote": 1.7},
    ]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["vote"] = df["vote"].astype(float)
    return df, "ejemplo"


df_raw, origen = load_data()


# ─────────────────────────────────
# SIDEBAR — FILTROS
# ─────────────────────────────────
with st.sidebar:
    st.title("🇨🇴 Colombia 2026")
    st.caption("Dashboard de encuestas presidenciales")
    st.divider()

    if origen == "parquet":
        st.success("Datos del pipeline (parquet)")
    elif origen == "csv":
        st.warning("Datos del pipeline (csv)")
    else:
        st.error(" Usando datos de ejemplo. Corre el notebook para datos reales.")

    st.divider()

    fuentes_disponibles = sorted(df_raw["source"].dropna().unique().tolist())
    fuentes_sel = st.multiselect("Encuestadoras", fuentes_disponibles, default=fuentes_disponibles)

    candidatos_disponibles = sorted(df_raw["candidate"].dropna().unique().tolist())
    candidatos_sel = st.multiselect("Candidatos", candidatos_disponibles, default=candidatos_disponibles)

    fecha_min = df_raw["date"].min().date()
    fecha_max = df_raw["date"].max().date()
    rango = st.date_input("Rango de fechas", value=(fecha_min, fecha_max))

    st.divider()
    st.caption(f"**Total registros:** {len(df_raw)}")
    st.caption(f"**Encuestadoras:** {df_raw['source'].nunique()}")
    st.caption(f"**Candidatos:** {df_raw['candidate'].nunique()}")


# ─────────────────────────────────
# APLICAR FILTROS
# ─────────────────────────────────
fecha_ini, fecha_fin = (rango[0], rango[1]) if len(rango) == 2 else (fecha_min, fecha_max)

df = df_raw[
    df_raw["source"].isin(fuentes_sel) &
    df_raw["candidate"].isin(candidatos_sel) &
    (df_raw["date"].dt.date >= fecha_ini) &
    (df_raw["date"].dt.date <= fecha_fin)
].copy()


# ─────────────────────────────────
# TÍTULO
# ─────────────────────────────────
st.title("🇨🇴 Colombia 2026 — Encuestas Presidenciales")
st.caption(f"Datos: {fecha_ini} → {fecha_fin} · {len(fuentes_sel)} encuestadoras · {len(df)} registros")
st.divider()


# ─────────────────────────────────
# MÉTRICAS — top candidatos
# ─────────────────────────────────
if not df.empty:
    top = df.groupby("candidate")["vote"].mean().sort_values(ascending=False).head(4)
    cols = st.columns(len(top))
    for i, (cand, val) in enumerate(top.items()):
        apellido = cand.split()[-1]
        n = df[df["candidate"] == cand]["source"].nunique()
        cols[i].metric(label=apellido, value=f"{val:.1f}%", help=f"{cand} · {n} encuestadora(s)")

st.divider()


# ─────────────────────────────────
# FILA 1 — Barras + Tabla
# ─────────────────────────────────
col1, col2 = st.columns([1.6, 1], gap="large")

with col1:
    st.subheader("Promedio de intención de voto")
    if not df.empty:
        promedios = (
            df.groupby("candidate")["vote"]
            .mean()
            .reset_index()
            .sort_values("vote", ascending=True)
        )
        promedios["color"] = promedios["candidate"].map(lambda c: COLORES.get(c, "#888888"))

        fig = go.Figure(go.Bar(
            y=promedios["candidate"],
            x=promedios["vote"],
            orientation="h",
            marker_color=promedios["color"],
            text=promedios["vote"].round(1).astype(str) + "%",
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>",
        ))
        fig.update_layout(
            xaxis=dict(title="Intención de voto (%)", range=[0, promedios["vote"].max() + 12]),
            yaxis=dict(title=""),
            margin=dict(l=0, r=40, t=10, b=0),
            height=320,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin datos para los filtros seleccionados.")

with col2:
    st.subheader("Resumen estadístico")
    if not df.empty:
        resumen = (
            df.groupby("candidate")["vote"]
            .agg(Promedio="mean", Mínimo="min", Máximo="max", Encuestas="count")
            .round(1)
            .sort_values("Promedio", ascending=False)
        )
        st.dataframe(resumen, use_container_width=True)
    else:
        st.info("Sin datos.")

st.divider()


# ─────────────────────────────────
# FILA 2 — Evolución + Por encuestadora
# ─────────────────────────────────
col3, col4 = st.columns(2, gap="large")

with col3:
    st.subheader("Evolución temporal")
    if not df.empty:
        fig2 = go.Figure()
        for cand in candidatos_sel:
            df_c = df[df["candidate"] == cand].sort_values("date")
            if df_c.empty:
                continue
            df_c_agg = df_c.groupby("date")["vote"].mean().reset_index()
            fig2.add_trace(go.Scatter(
                x=df_c_agg["date"],
                y=df_c_agg["vote"],
                mode="lines+markers",
                name=cand.split()[-1],
                line=dict(color=COLORES.get(cand, "#888"), width=2),
                marker=dict(size=6),
                hovertemplate=f"<b>{cand}</b><br>%{{x|%d %b}}: %{{y:.1f}}%<extra></extra>",
            ))
        fig2.update_layout(
            xaxis=dict(title="", tickformat="%b %Y"),
            yaxis=dict(title="Intención de voto (%)", ticksuffix="%"),
            legend=dict(title=""),
            margin=dict(l=0, r=0, t=10, b=0),
            height=320,
            hovermode="x unified",
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sin datos.")

with col4:
    st.subheader("Resultados por encuestadora")
    if not df.empty:
        candidatos_top5 = (
            df.groupby("candidate")["vote"]
            .mean()
            .sort_values(ascending=False)
            .head(5)
            .index.tolist()
        )
        df_comp = df[df["candidate"].isin(candidatos_top5)]
        fig3 = px.bar(
            df_comp,
            x="candidate", y="vote", color="source",
            barmode="group",
            labels={"vote": "Intención (%)", "candidate": "", "source": "Encuestadora"},
        )
        fig3.update_layout(
            xaxis=dict(tickangle=-20),
            yaxis=dict(title="Intención de voto (%)", ticksuffix="%"),
            legend=dict(title=""),
            margin=dict(l=0, r=0, t=10, b=0),
            height=320,
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Sin datos.")

st.divider()


# ─────────────────────────────────
# DATOS CRUDOS + DESCARGA
# ─────────────────────────────────
st.subheader("Datos completos")
if not df.empty:
    df_show = df.copy()
    df_show["date"] = df_show["date"].dt.strftime("%d %b %Y")
    df_show = df_show.rename(columns={
        "candidate": "Candidato",
        "vote": "Intención (%)",
        "source": "Encuestadora",
        "date": "Fecha",
    })
    st.dataframe(
        df_show[["Candidato", "Intención (%)", "Encuestadora", "Fecha"]],
        use_container_width=True,
        hide_index=True,
    )
    csv = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="⬇ Descargar CSV",
        data=csv,
        file_name="colombia_2026_filtrado.csv",
        mime="text/csv",
    )
else:
    st.info("No hay datos para los filtros seleccionados.")

st.caption("Fuentes: AtlasIntel, CNC, GAD3, Guarumo, ASCOA · Pipeline: ColombiaScrapp.ipynb")
