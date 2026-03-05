
import streamlit as st
import numpy as np
import pandas as pd
import scipy.stats as stats
import plotly.graph_objects as go
import plotly.io as pio
import io, json
from plotly.subplots import make_subplots

# ── Configuración de página ──────────────────────────────────
st.set_page_config(
    page_title="Homogeneidad ISO 17034",
    page_icon="🧪",
    layout="wide"
)

# ── Estilo CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    .main-title  {font-size:2rem; font-weight:700; color:#1a5276; margin-bottom:0}
    .sub-title   {font-size:1rem; color:#555; margin-bottom:1.5rem}
    .card        {background:#f0f4f8; border-radius:12px; padding:1.2rem 1.5rem; margin-bottom:1rem}
    .metric-box  {background:#ffffff; border-left:5px solid #1a5276;
                  border-radius:8px; padding:0.8rem 1.2rem; margin:0.4rem 0}
    .homogeneo   {background:#eafaf1; border-left:5px solid #27ae60;
                  border-radius:8px; padding:1rem 1.5rem; font-size:1.1rem; font-weight:600; color:#1e8449}
    .heterogeneo {background:#fdedec; border-left:5px solid #e74c3c;
                  border-radius:8px; padding:1rem 1.5rem; font-size:1.1rem; font-weight:600; color:#922b21}
    .section-hdr {color:#1a5276; font-size:1.15rem; font-weight:600;
                  border-bottom:2px solid #aed6f1; padding-bottom:4px; margin-top:1.2rem}
</style>
""", unsafe_allow_html=True)

# ── Encabezado ───────────────────────────────────────────────
st.markdown('<p class="main-title">🧪 Evaluación de Homogeneidad</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">ANOVA de una vía · ISO 17034:2017 §9.4 · ICA – Subgerencia de Análisis y Diagnóstico</p>', unsafe_allow_html=True)

# ── Sidebar: configuración ───────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/ICA_Colombia_logo.svg/320px-ICA_Colombia_logo.svg.png",
             width=160, caption="ICA Colombia")
    st.markdown("---")
    st.markdown("### ⚙️ Parámetros")
    alpha = st.select_slider("Nivel de significancia (α)",
                             options=[0.01, 0.05, 0.10], value=0.05)
    col_unidad   = st.text_input("Nombre columna Unidad",   value="Unidad")
    col_medicion = st.text_input("Nombre columna Medicion", value="Medicion")
    st.markdown("---")
    st.markdown("### 📥 Plantilla Excel")
    plantilla = pd.DataFrame({
        "Unidad":   [1,1,1,2,2,2,3,3,3],
        "Medicion": [21.0,21.0,20.5,20.0,20.5,21.0,21.0,20.0,20.5]
    })
    buf = io.BytesIO()
    plantilla.to_excel(buf, index=False)
    st.download_button("⬇️ Descargar plantilla",
                       data=buf.getvalue(),
                       file_name="plantilla_homogeneidad.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown("---")
    st.caption("Basado en ISO 17034:2017 e ISO 13528:2022")

# ── Pestañas de entrada de datos ────────────────────────────
tab_excel, tab_manual = st.tabs(["📁 Cargar Excel", "✏️ Ingresar manualmente"])

df = None

with tab_excel:
    st.markdown('<p class="section-hdr">Carga tu archivo Excel</p>', unsafe_allow_html=True)
    st.info("El archivo debe tener dos columnas: **Unidad** y **Medicion** (los nombres pueden ajustarse en la barra lateral).")
    archivo = st.file_uploader("Selecciona el archivo .xlsx o .xls",
                               type=["xlsx","xls"], key="file_up")
    if archivo:
        try:
            df_raw = pd.read_excel(archivo)
            st.success(f"Archivo cargado: **{archivo.name}** — {len(df_raw)} filas, {len(df_raw.columns)} columnas")
            st.dataframe(df_raw.head(30), use_container_width=True)
            if col_unidad in df_raw.columns and col_medicion in df_raw.columns:
                df = df_raw[[col_unidad, col_medicion]].dropna()
                df[col_medicion] = pd.to_numeric(df[col_medicion], errors="coerce")
                df.dropna(inplace=True)
                df.columns = ["Unidad","Medicion"]
            else:
                st.error(f"No se encontraron las columnas '{col_unidad}' y '{col_medicion}'. "
                         f"Columnas disponibles: {list(df_raw.columns)}")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

with tab_manual:
    st.markdown('<p class="section-hdr">Ingreso manual de datos</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        n_unidades = st.number_input("Número de unidades", min_value=2, max_value=50, value=10, step=1)
    with c2:
        n_reps = st.number_input("Réplicas por unidad", min_value=2, max_value=10, value=3, step=1)

    st.markdown("**Ingresa los valores en la tabla** (haz doble clic en una celda para editar):")
    cols_tabla = [f"Rep {j+1}" for j in range(n_reps)]
    df_editor = pd.DataFrame(
        np.full((n_unidades, n_reps), np.nan),
        index=[f"Unidad {i+1}" for i in range(n_unidades)],
        columns=cols_tabla
    )
    df_editado = st.data_editor(df_editor, use_container_width=True,
                                num_rows="fixed", key="editor")

    if st.button("▶ Usar datos manuales", type="primary"):
        rows = []
        for i, idx in enumerate(df_editado.index):
            for j, col in enumerate(df_editado.columns):
                val = df_editado.loc[idx, col]
                if pd.notna(val):
                    rows.append({"Unidad": i+1, "Medicion": float(val)})
        if rows:
            df = pd.DataFrame(rows)
            st.success(f"✅ Datos cargados: {len(df)} observaciones, {df['Unidad'].nunique()} unidades")
        else:
            st.warning("Ingresa al menos algunos valores antes de continuar.")

# ── ANÁLISIS ─────────────────────────────────────────────────
if df is not None and len(df) > 0:
    st.markdown("---")
    st.markdown("## 📊 Resultados del Análisis")

    unidades   = sorted(df["Unidad"].unique())
    n          = len(unidades)
    rep_counts = df.groupby("Unidad")["Medicion"].count()
    m_vals     = rep_counts.values
    balanced   = len(set(m_vals)) == 1
    m_eff      = float(m_vals[0]) if balanced else (
        (len(df)**2 - sum(rep_counts**2)) / ((n - 1) * len(df))
    )

    grand_mean = df["Medicion"].mean()
    unit_means = df.groupby("Unidad")["Medicion"].mean()

    SS_entre = sum(rep_counts[u] * (unit_means[u] - grand_mean)**2 for u in unidades)
    gl_entre = n - 1
    CM_entre = SS_entre / gl_entre

    SS_res = sum(
        np.sum((df[df["Unidad"]==u]["Medicion"].values - unit_means[u])**2)
        for u in unidades
    )
    gl_res = len(df) - n
    CM_res = SS_res / gl_res

    F_calc  = CM_entre / CM_res
    F_crit  = stats.f.ppf(1 - alpha, gl_entre, gl_res)
    p_valor = stats.f.sf(F_calc, gl_entre, gl_res)

    s_bb_sq = (CM_entre - CM_res) / m_eff
    if s_bb_sq > 0:
        u_hom    = np.sqrt(s_bb_sq)
        u_metodo = "s²bb > 0 → √[(CM_entre − CM_res)/m]"
    else:
        u_hom    = np.sqrt(CM_res / m_eff)
        u_metodo = "s²bb ≤ 0 → conservadora √[CM_res/m]"

    heterogeneo = F_calc > F_crit

    # ── Tarjeta de decisión ─────────────────────────────────
    if heterogeneo:
        st.markdown(
            f'<div class="heterogeneo">⚠️ LOTE HETEROGÉNEO — F calc ({F_calc:.4f}) > F crit ({F_crit:.4f}) | p = {p_valor:.5f}</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="homogeneo">✅ LOTE HOMOGÉNEO — F calc ({F_calc:.4f}) ≤ F crit ({F_crit:.4f}) | p = {p_valor:.5f}</div>',
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Métricas clave ──────────────────────────────────────
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("N° unidades",       n)
    col2.metric("Réplicas/unidad",   f"{m_eff:.1f}" if not balanced else int(m_eff))
    col3.metric("Media global",      f"{grand_mean:.5f}")
    col4.metric("u_hom (absoluta)",  f"{u_hom:.6f}")
    col5.metric("u_hom DER%",        f"{u_hom/grand_mean*100:.4f}%")

    # ── Tabla ANOVA ─────────────────────────────────────────
    st.markdown('<p class="section-hdr">Tabla ANOVA</p>', unsafe_allow_html=True)
    anova_df = pd.DataFrame({
        "Fuente":           ["Entre unidades", "Residual (dentro)", "Total"],
        "Suma de Cuadrados": [round(SS_entre,6), round(SS_res,6), round(SS_entre+SS_res,6)],
        "Grados de libertad":[gl_entre, gl_res, gl_entre+gl_res],
        "Cuadrado Medio":   [round(CM_entre,6), round(CM_res,6), "—"],
        "F calculado":      [round(F_calc,4), "—", "—"],
        f"F crítico (α={alpha})": [round(F_crit,4), "—", "—"],
        "p-valor":          [round(p_valor,6), "—", "—"],
    })
    st.dataframe(anova_df, use_container_width=True, hide_index=True)

    # ── Incertidumbre ───────────────────────────────────────
    st.markdown('<p class="section-hdr">Incertidumbre por Homogeneidad — ISO 17034 §9.4</p>', unsafe_allow_html=True)
    ci1, ci2, ci3 = st.columns(3)
    ci1.metric("s²bb (varianza entre unidades)", f"{max(s_bb_sq,0):.8f}")
    ci2.metric("u_hom",   f"{u_hom:.6f}")
    ci3.metric("u_hom / x̄ × 100", f"{u_hom/grand_mean*100:.4f} %")
    st.caption(f"Método aplicado: {u_metodo}")

    # ── Tabla de medias por unidad ──────────────────────────
    with st.expander("📋 Ver estadísticos por unidad"):
        tbl = pd.DataFrame({
            "Unidad": [str(u) for u in unidades],
            "N réplicas": [int(rep_counts[u]) for u in unidades],
            "Media": [round(unit_means[u],6) for u in unidades],
            "Desv. estándar": [round(df[df["Unidad"]==u]["Medicion"].std(ddof=1),6) for u in unidades],
            "Mín": [df[df["Unidad"]==u]["Medicion"].min() for u in unidades],
            "Máx": [df[df["Unidad"]==u]["Medicion"].max() for u in unidades],
        })
        st.dataframe(tbl, use_container_width=True, hide_index=True)

    # ── Gráficos ────────────────────────────────────────────
    st.markdown('<p class="section-hdr">Gráficos</p>', unsafe_allow_html=True)
    gc1, gc2 = st.columns(2)
    colors = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd",
              "#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf",
              "#aec7e8","#ffbb78","#98df8a","#ff9896","#c5b0d5"]

    # Scatter
    fig1 = go.Figure()
    for i, u in enumerate(unidades):
        vals = df[df["Unidad"]==u]["Medicion"].values
        c = colors[i % len(colors)]
        fig1.add_trace(go.Scatter(
            x=[str(u)]*len(vals), y=vals, mode="markers",
            marker=dict(size=10, opacity=0.5, color=c), showlegend=False
        ))
        fig1.add_trace(go.Scatter(
            x=[str(u)], y=[unit_means[u]], mode="markers",
            marker=dict(size=14, symbol="diamond", color=c,
                        line=dict(width=2, color="white")),
            showlegend=False
        ))
    fig1.add_hline(y=grand_mean, line_dash="dash", line_color="gray",
                   annotation_text=f"x̄={grand_mean:.4f}",
                   annotation_position="top right")
    fig1.update_layout(
        title="Réplicas por unidad (◆ = media)",
        xaxis_title="Unidad", yaxis_title="Valor medido",
        height=400, margin=dict(t=50,b=50,l=60,r=30)
    )
    gc1.plotly_chart(fig1, use_container_width=True)

    # Barras con u_hom
    fig2 = go.Figure()
    for i, u in enumerate(unidades):
        fig2.add_trace(go.Bar(
            x=[str(u)], y=[unit_means[u]],
            marker_color=colors[i % len(colors)],
            showlegend=False,
            error_y=dict(type="constant", value=u_hom,
                         visible=True, color="#999", thickness=1.5, width=8)
        ))
    fig2.add_hline(y=grand_mean, line_dash="dot", line_color="gray",
                   annotation_text=f"x̄={grand_mean:.4f}",
                   annotation_position="top right")
    fig2.update_layout(
        title=f"Medias por unidad ± u_hom ({u_hom:.5f})",
        xaxis_title="Unidad", yaxis_title="Media",
        height=400, margin=dict(t=50,b=50,l=60,r=30),
        yaxis=dict(range=[grand_mean - 5*u_hom, grand_mean + 5*u_hom])
    )
    gc2.plotly_chart(fig2, use_container_width=True)

    # ── Descargas ────────────────────────────────────────────
    st.markdown('<p class="section-hdr">Exportar resultados</p>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)

    resumen = pd.DataFrame({
        "Parámetro": ["N unidades","Réplicas/unidad","Media global",
                      "CM_entre","CM_res","F_calculado",
                      f"F_critico_alpha{alpha}","p_valor","Decisión",
                      "s_bb_cuadrado","u_hom","u_hom_DER_pct",
                      "Método u_hom"],
        "Valor": [n, round(m_eff,2), round(grand_mean,8),
                  round(CM_entre,8), round(CM_res,8),
                  round(F_calc,6), round(F_crit,6), round(p_valor,6),
                  "HETEROGENEO" if heterogeneo else "HOMOGENEO",
                  round(max(s_bb_sq,0),10), round(u_hom,8),
                  round(u_hom/grand_mean*100,6), u_metodo]
    })
    buf_csv = resumen.to_csv(index=False).encode("utf-8")
    d1.download_button("⬇️ Descargar resumen (.csv)", data=buf_csv,
                       file_name="resultados_homogeneidad.csv", mime="text/csv")

    buf_xl = io.BytesIO()
    with pd.ExcelWriter(buf_xl, engine="openpyxl") as writer:
        resumen.to_excel(writer,   sheet_name="Resumen",   index=False)
        anova_df.to_excel(writer,  sheet_name="ANOVA",     index=False)
        tbl.to_excel(writer,       sheet_name="Por unidad",index=False)
        df.to_excel(writer,        sheet_name="Datos brutos", index=False)
    d2.download_button("⬇️ Descargar reporte completo (.xlsx)",
                       data=buf_xl.getvalue(),
                       file_name="reporte_homogeneidad.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.info("👈 Carga un archivo Excel o ingresa los datos manualmente para comenzar el análisis.")

# ── Pie de página ────────────────────────────────────────────
st.markdown("---")
st.caption("ICA – Subgerencia de Análisis y Diagnóstico | Evaluación de homogeneidad ISO 17034:2017 §9.4 | Implementado con Streamlit")
