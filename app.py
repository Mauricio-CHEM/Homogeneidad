
import streamlit as st
import numpy as np
import pandas as pd
import scipy.stats as stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io, json, textwrap

# ════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DE PÁGINA
# ════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Homogeneidad MR/EA · IIAD-LANIA · ICA",
    page_icon="🧪", layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-title{font-size:2rem;font-weight:700;color:#1a5e36;margin-bottom:0}
.sub-title{font-size:.95rem;color:#666;margin-bottom:1.2rem}
.card{background:#f0f8f2;border-radius:10px;padding:1rem 1.4rem;margin-bottom:.8rem}
.theory-box{background:#eafaf1;border-left:5px solid #27ae60;
            border-radius:6px;padding:1rem 1.4rem;margin:.6rem 0;font-size:.93rem}
.warn-box{background:#fef9e7;border-left:5px solid #f39c12;
          border-radius:6px;padding:.9rem 1.3rem;margin:.6rem 0}
.ok-box{background:#eafaf1;border-left:5px solid #27ae60;
        border-radius:6px;padding:.9rem 1.3rem;margin:.6rem 0;font-weight:600;color:#1e8449}
.err-box{background:#fdedec;border-left:5px solid #e74c3c;
         border-radius:6px;padding:.9rem 1.3rem;margin:.6rem 0;font-weight:600;color:#922b21}
.section-hdr{color:#1a5e36;font-size:1.05rem;font-weight:600;
             border-bottom:2px solid #a9dfbf;padding-bottom:3px;margin-top:1rem}
.interp{background:#f8f9fa;border-radius:8px;padding:.9rem 1.3rem;
        font-size:.9rem;color:#333;margin-top:.5rem}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  BANNER INSTITUCIONAL
# ════════════════════════════════════════════════════════════
# Cargar logo institucional (coloca el archivo en assets/logo_ica.png)
import base64, os

def _cargar_logo(ruta: str) -> str:
    """Retorna la imagen como string base64 para incrustar en HTML."""
    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

_logo_b64 = _cargar_logo("assets/logo_ica.png")
_logo_html = (
    f'<img src="data:image/png;base64,{_logo_b64}" \'
    'style="height:64px;width:auto;object-fit:contain;filter:brightness(0) invert(1);">\'
) if _logo_b64 else '<span style="font-size:2.6rem">🧪</span>'

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #1a5e36 0%, #27ae60 60%, #2ecc71 100%);
    border-radius: 10px;
    padding: 1rem 2rem;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 1.4rem;
    box-shadow: 0 3px 10px rgba(0,0,0,0.15);
">
    <div style="flex-shrink:0">{_logo_html}</div>
    <div style="flex:1">
        <div style="color:white;font-size:1.25rem;font-weight:700;line-height:1.35">
            Evaluación de la Homogeneidad de Materiales de Referencia<br>
            e Ítems de Ensayo de Aptitud
        </div>
        <div style="color:#d5f5e3;font-size:.88rem;margin-top:5px">
            Área IIAD &nbsp;·&nbsp; LANIA &nbsp;|&nbsp; ISO 17034:2017 §9.4
            &nbsp;|&nbsp; Instituto Colombiano Agropecuario (ICA)
            &nbsp;—&nbsp; Subgerencia de Análisis y Diagnóstico
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo en sidebar
    import base64, os
    def _logo_sidebar(ruta):
        if os.path.exists(ruta):
            with open(ruta,"rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            st.markdown(
                f'<img src="data:image/png;base64,{b64}" \'
                'style="max-width:100%;height:auto;margin-bottom:6px;">',
                unsafe_allow_html=True)
        else:
            st.markdown("### 🌿 ICA — Área IIAD · LANIA")
    _logo_sidebar("assets/logo_ica.png")
    st.markdown("**Homogeneidad ISO 17034:2017**")
    st.markdown("---")
    st.markdown("#### ⚙️ Parámetros estadísticos")
    alpha       = st.select_slider("Nivel de significancia (α)", [0.01,0.05,0.10], value=0.05)
    col_unidad  = st.text_input("Columna identificadora de unidades", "Unidad")
    st.markdown("---")
    st.markdown("#### 🎯 Incertidumbre objetivo")
    usar_u_obj  = st.checkbox("Comparar u_hom con u objetivo", value=False)
    u_objetivo  = None
    u_obj_tipo  = "absoluta"
    if usar_u_obj:
        u_obj_tipo = st.radio("Tipo de incertidumbre objetivo",
                              ["absoluta","relativa (%)"], horizontal=True)
        u_objetivo = st.number_input(
            "Valor de u objetivo" + (" (%)" if "relativa" in u_obj_tipo else ""),
            min_value=0.0, value=0.5, format="%.6f", step=0.001
        )
        st.caption("Criterio ISO Guide 35: u_hom < u_obj/3 → contribución despreciable")
    st.markdown("---")
    # Plantilla multi-componente
    st.markdown("#### 📥 Plantilla Excel")
    plantilla = pd.DataFrame({
        "Unidad": [1,1,1,2,2,2,3,3,3],
        "Molecula_A": [21.3,21.1,21.5,20.8,20.5,21.0,21.2,21.4,21.1],
        "Molecula_B": [15.2,15.4,15.1,14.9,15.3,15.0,15.2,15.1,15.3],
        "Molecula_C": [8.1, 8.3, 8.0, 8.2, 8.1, 8.4, 8.0, 8.2, 8.1],
    })
    buf_t = io.BytesIO()
    plantilla.to_excel(buf_t, index=False)
    st.download_button("⬇️ Descargar plantilla multi-componente",
                       data=buf_t.getvalue(),
                       file_name="plantilla_homogeneidad_multi.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.caption("Formato: columna 'Unidad' + una columna por molécula/componente. Cada fila = una réplica.")

# ════════════════════════════════════════════════════════════
#  NAVEGACIÓN POR PÁGINAS
# ════════════════════════════════════════════════════════════
pagina = st.radio("", ["🏠 Inicio e Instrucciones",
                       "📁 Ingreso de Datos",
                       "📊 Resultados por Componente",
                       "📋 Resumen General"],
                  horizontal=True, label_visibility="collapsed")
st.markdown("---")

# ════════════════════════════════════════════════════════════
#  PÁGINA 1 — INICIO E INSTRUCCIONES
# ════════════════════════════════════════════════════════════
if pagina == "🏠 Inicio e Instrucciones":
    st.markdown('<p class="main-title">Evaluación de la Homogeneidad</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">ISO 17034:2017 §9.4 &nbsp;·&nbsp; ISO Guide 35:2017 &nbsp;·&nbsp; Área IIAD · LANIA · ICA</p>', unsafe_allow_html=True)

    c1, c2 = st.columns([1.1, 1])
    with c1:
        st.markdown("### 📖 ¿Qué es el estudio de homogeneidad?")
        st.markdown("""<div class="theory-box">
        El estudio de homogeneidad evalúa si las unidades de un lote de material de referencia
        son <b>estadísticamente equivalentes entre sí</b>, es decir, que cualquier unidad
        entregada a un usuario tiene esencialmente el mismo valor de propiedad.<br><br>
        Según <b>ISO 17034:2017 §9.4</b>, el productor de MR debe demostrar la homogeneidad
        del lote antes de asignar el valor de propiedad certificado, y cuantificar la
        <b>incertidumbre asociada a la heterogeneidad (u_hom)</b> para incorporarla
        en la incertidumbre expandida del certificado.
        </div>""", unsafe_allow_html=True)

        st.markdown("### 🔬 Diseño experimental recomendado")
        st.markdown("""<div class="theory-box">
        <ul>
        <li><b>Mínimo 10 unidades</b> seleccionadas aleatoriamente del lote</li>
        <li><b>Mínimo 2 réplicas independientes</b> por unidad (se recomiendan 3)</li>
        <li>Las réplicas deben ser <b>mediciones independientes</b>, no duplicados instrumentales</li>
        <li>El analista debe ser el mismo para todas las mediciones (o randomizar el orden)</li>
        <li>El método debe estar <b>validado y bajo control estadístico</b></li>
        </ul>
        </div>""", unsafe_allow_html=True)

        st.markdown("### 📐 Fundamento estadístico — ANOVA de una vía")
        st.markdown("""<div class="theory-box">
        Se plantea un modelo lineal de efectos fijos:<br><br>
        <code>x_ij = μ + α_i + ε_ij</code><br><br>
        donde <code>μ</code> es la media global, <code>α_i</code> el efecto de la unidad <i>i</i>,
        y <code>ε_ij ~ N(0, σ²)</code> el error aleatorio.<br><br>
        <b>Tabla ANOVA:</b><br>
        <table style="width:100%;font-size:.85rem">
        <tr><th>Fuente</th><th>SC</th><th>gl</th><th>CM</th></tr>
        <tr><td>Entre unidades</td>
            <td>m·Σ(x̄_i − x̄)²</td><td>n−1</td><td>CM_entre</td></tr>
        <tr><td>Residual</td>
            <td>ΣΣ(x_ij − x̄_i)²</td><td>n(m−1)</td><td>CM_res</td></tr>
        </table>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown("### 📊 Hipótesis del análisis")
        st.markdown("""<div class="warn-box">
        <b>H₀ (Hipótesis nula):</b> No existe diferencia estadísticamente significativa
        entre las medias de las unidades del lote.<br>
        <i>Las unidades son homogéneas: α_1 = α_2 = ... = α_n = 0</i><br><br>
        <b>H₁ (Hipótesis alternativa):</b> Al menos una unidad difiere significativamente
        de las demás.<br>
        <i>Existe heterogeneidad: ∃ i,j tal que α_i ≠ α_j</i>
        </div>""", unsafe_allow_html=True)

        st.markdown("### ✅ Interpretación de resultados")
        st.markdown("""<div class="theory-box">
        <b>Si F_calc ≤ F_crit (p > α) → HOMOGÉNEO</b><br>
        No hay evidencia de diferencias entre unidades. Se calcula u_hom como estimación
        conservadora: <code>u_hom = √(CM_res / m)</code><br><br>
        <b>Si F_calc > F_crit (p ≤ α) → HETEROGÉNEO</b><br>
        Existe variabilidad significativa entre unidades. Se cuantifica:
        <code>u_hom = √(s²_bb)</code> donde <code>s²_bb = (CM_entre − CM_res)/m</code><br><br>
        <b>Criterio de aptitud (ISO Guide 35):</b><br>
        <ul>
        <li>u_hom < u_obj/3 → contribución <b>despreciable</b> ✅</li>
        <li>u_hom < u_obj → contribución <b>aceptable</b> pero se propaga ⚠️</li>
        <li>u_hom ≥ u_obj → <b>lote inaceptable</b> para el uso previsto ❌</li>
        </ul>
        </div>""", unsafe_allow_html=True)

        st.markdown("### 🔍 Análisis de residuales")
        st.markdown("""<div class="theory-box">
        La validez del ANOVA requiere verificar los <b>supuestos del modelo</b>:<br><br>
        <b>1. Normalidad de residuales:</b> Prueba Shapiro-Wilk (H₀: residuales normales).
        Si p > α: supuesto cumplido.<br><br>
        <b>2. Homocedasticidad (varianzas iguales):</b> Prueba de Bartlett (H₀: σ²_1=...=σ²_n).
        Si p > α: varianzas homogéneas.<br><br>
        <b>3. Gráfico Q-Q:</b> Los puntos deben seguir la línea diagonal.
        Desviaciones indican no-normalidad.<br><br>
        <b>4. Residuales vs valores ajustados:</b> Sin patrones sistemáticos → modelo adecuado.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🗂️ Formato del archivo Excel")
    st.markdown("""<div class="card">
    El archivo debe tener una columna <b>Unidad</b> (identificador de cada unidad del lote)
    y <b>una columna por cada componente/molécula</b> a evaluar. Cada fila representa
    una réplica independiente.
    </div>""", unsafe_allow_html=True)
    ejemplo_fmt = pd.DataFrame({
        "Unidad":     [1,1,1,2,2,2,"..."],
        "Clorpirifos":[21.3,21.1,21.5,20.8,20.5,21.0,"..."],
        "Cipermetrina":[15.2,15.4,15.1,14.9,15.3,15.0,"..."],
        "Malatión":   [8.1,8.3,8.0,8.2,8.1,8.4,"..."],
        "... (hasta 37)":[".",".",".",".",".",".","."]
    })
    st.dataframe(ejemplo_fmt, hide_index=True, use_container_width=True)

    st.markdown("### 🚀 Pasos para usar el aplicativo")
    pasos = [
        "**Descarga la plantilla Excel** desde la barra lateral y completa con tus datos",
        "**Ve a 'Ingreso de Datos'** y carga tu archivo o ingresa los datos manualmente",
        "**Ve a 'Resultados por Componente'** y selecciona la molécula a analizar",
        "**Revisa la tabla ANOVA**, la decisión, los residuales y el valor de u_hom",
        "**Ve a 'Resumen General'** para ver todos los componentes en una sola tabla",
        "**Exporta el reporte** completo en Excel con un clic",
    ]
    for i, p in enumerate(pasos, 1):
        st.markdown(f"**{i}.** {p}")

# ════════════════════════════════════════════════════════════
#  FUNCIÓN PRINCIPAL DE ANÁLISIS
# ════════════════════════════════════════════════════════════
def analizar_componente(df_comp, componente, alpha, u_objetivo, u_obj_tipo, grand_mean_override=None):
    """Recibe df con columnas [Unidad, Valor]. Retorna dict de resultados."""
    df = df_comp.copy()
    unidades   = sorted(df["Unidad"].unique())
    n          = len(unidades)
    rep_counts = df.groupby("Unidad")["Valor"].count()
    m_vals     = rep_counts.values
    balanced   = len(set(m_vals)) == 1
    m_eff      = float(m_vals[0]) if balanced else (
        (len(df)**2 - sum(rep_counts**2)) / ((n-1)*len(df))
    )
    grand_mean = df["Valor"].mean()
    unit_means = df.groupby("Unidad")["Valor"].mean()

    SS_entre = sum(rep_counts[u]*(unit_means[u]-grand_mean)**2 for u in unidades)
    gl_entre = n - 1
    CM_entre = SS_entre / gl_entre
    SS_res   = sum(np.sum((df[df["Unidad"]==u]["Valor"].values - unit_means[u])**2) for u in unidades)
    gl_res   = len(df) - n
    CM_res   = SS_res / gl_res if gl_res > 0 else np.nan

    F_calc   = CM_entre / CM_res if CM_res and CM_res > 0 else np.nan
    F_crit   = stats.f.ppf(1-alpha, gl_entre, gl_res)
    p_valor  = stats.f.sf(F_calc, gl_entre, gl_res) if not np.isnan(F_calc) else np.nan

    s_bb_sq  = (CM_entre - CM_res) / m_eff if CM_res else np.nan
    if s_bb_sq is not None and s_bb_sq > 0:
        u_hom    = np.sqrt(s_bb_sq)
        u_metodo = "s²bb > 0 → √[(CM_entre − CM_res) / m]"
    else:
        u_hom    = np.sqrt(CM_res / m_eff) if CM_res else np.nan
        u_metodo = "s²bb ≤ 0 → conservadora √[CM_res / m]"

    heterogeneo = bool(F_calc > F_crit) if not np.isnan(F_calc) else False

    # Residuales
    residuales = []
    fitted     = []
    for u in unidades:
        vals = df[df["Unidad"]==u]["Valor"].values
        for v in vals:
            residuales.append(v - unit_means[u])
            fitted.append(unit_means[u])
    residuales = np.array(residuales)
    fitted     = np.array(fitted)

    # Pruebas sobre residuales
    sw_stat, sw_p = stats.shapiro(residuales) if len(residuales) >= 3 else (np.nan, np.nan)
    grupos = [df[df["Unidad"]==u]["Valor"].values for u in unidades]
    if all(len(g) > 1 for g in grupos):
        bt_stat, bt_p = stats.bartlett(*grupos)
    else:
        bt_stat, bt_p = np.nan, np.nan

    # Comparación u_hom vs u_objetivo
    u_comp = None
    if u_objetivo is not None and not np.isnan(u_hom):
        if "relativa" in u_obj_tipo:
            u_obj_abs = grand_mean * u_objetivo / 100
        else:
            u_obj_abs = u_objetivo
        ratio = u_hom / u_obj_abs if u_obj_abs > 0 else np.nan
        if   ratio < 1/3:    u_comp = ("despreciable", "✅", ratio)
        elif ratio < 1.0:    u_comp = ("aceptable",    "⚠️", ratio)
        else:                u_comp = ("inaceptable",  "❌", ratio)
    else:
        u_obj_abs = None

    return dict(
        componente=componente, n=n, m_eff=m_eff, balanced=balanced,
        grand_mean=grand_mean, unit_means=unit_means, rep_counts=rep_counts,
        SS_entre=SS_entre, gl_entre=gl_entre, CM_entre=CM_entre,
        SS_res=SS_res, gl_res=gl_res, CM_res=CM_res,
        F_calc=F_calc, F_crit=F_crit, p_valor=p_valor,
        s_bb_sq=max(s_bb_sq,0) if s_bb_sq is not None else 0,
        u_hom=u_hom, u_metodo=u_metodo, heterogeneo=heterogeneo,
        residuales=residuales, fitted=fitted, unidades=unidades,
        sw_stat=sw_stat, sw_p=sw_p, bt_stat=bt_stat, bt_p=bt_p,
        u_comp=u_comp, u_obj_abs=u_obj_abs, df_comp=df
    )

# ════════════════════════════════════════════════════════════
#  CARGA Y ALMACENAMIENTO DE DATOS
# ════════════════════════════════════════════════════════════
if "df_datos" not in st.session_state:
    st.session_state["df_datos"] = None
if "componentes" not in st.session_state:
    st.session_state["componentes"] = []

# ════════════════════════════════════════════════════════════
#  PÁGINA 2 — INGRESO DE DATOS
# ════════════════════════════════════════════════════════════
elif pagina == "📁 Ingreso de Datos":
    st.markdown("## 📁 Ingreso de Datos")
    tab_xl, tab_man = st.tabs(["📂 Cargar Excel", "✏️ Ingresar manualmente"])

    with tab_xl:
        st.info("**Formato esperado:** columna `Unidad` + una columna por componente. "
                "Cada fila = una réplica independiente. Se admiten diseños balanceados y desbalanceados.")
        archivo = st.file_uploader("Selecciona archivo .xlsx o .xls", type=["xlsx","xls"])
        if archivo:
            try:
                df_raw = pd.read_excel(archivo)
                if col_unidad not in df_raw.columns:
                    st.error(f"Columna '{col_unidad}' no encontrada. Columnas disponibles: {list(df_raw.columns)}")
                else:
                    componentes_det = [c for c in df_raw.columns if c != col_unidad]
                    st.success(f"✅ **{archivo.name}** cargado — "
                               f"{len(df_raw)} filas · {len(componentes_det)} componente(s) detectado(s)")
                    st.markdown(f"**Componentes:** {', '.join(componentes_det)}")
                    st.dataframe(df_raw.head(20), use_container_width=True, hide_index=True)
                    # Limpiar y guardar
                    df_raw[col_unidad] = df_raw[col_unidad].astype(str)
                    for c in componentes_det:
                        df_raw[c] = pd.to_numeric(df_raw[c], errors="coerce")
                    st.session_state["df_datos"]    = df_raw
                    st.session_state["componentes"] = componentes_det
                    st.session_state["col_unidad"]  = col_unidad
                    st.success("Datos listos. Ve a **📊 Resultados por Componente** para el análisis.")
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

    with tab_man:
        c1, c2, c3 = st.columns(3)
        n_un  = c1.number_input("Unidades", 2, 50, 10, key="n_un")
        n_rep = c2.number_input("Réplicas/unidad", 2, 10, 3, key="n_rep")
        n_comp= c3.number_input("N° componentes", 1, 37, 1, key="n_comp")
        comp_names = []
        cols_n = st.columns(min(n_comp, 6))
        for i in range(n_comp):
            comp_names.append(cols_n[i%6].text_input(f"Nombre componente {i+1}", f"Componente_{i+1}", key=f"cn{i}"))
        rows_base = []
        for i in range(n_un):
            for j in range(n_rep):
                rows_base.append({col_unidad: str(i+1), **{c: np.nan for c in comp_names}})
        df_editor = pd.DataFrame(rows_base)
        st.caption("Haz doble clic en una celda para editar:")
        df_edit = st.data_editor(df_editor, use_container_width=True, hide_index=True, key="man_editor")
        if st.button("▶ Usar datos manuales", type="primary"):
            df_edit[col_unidad] = df_edit[col_unidad].astype(str)
            for c in comp_names:
                df_edit[c] = pd.to_numeric(df_edit[c], errors="coerce")
            st.session_state["df_datos"]    = df_edit
            st.session_state["componentes"] = comp_names
            st.session_state["col_unidad"]  = col_unidad
            st.success(f"✅ {len(df_edit)} observaciones · {len(comp_names)} componente(s). "
                       "Ve a **📊 Resultados por Componente**.")

# ════════════════════════════════════════════════════════════
#  PÁGINA 3 — RESULTADOS POR COMPONENTE
# ════════════════════════════════════════════════════════════
elif pagina == "📊 Resultados por Componente":
    if st.session_state["df_datos"] is None:
        st.warning("⚠️ Primero carga tus datos en la página **📁 Ingreso de Datos**.")
        st.stop()

    df_datos    = st.session_state["df_datos"]
    componentes = st.session_state["componentes"]
    col_uid     = st.session_state.get("col_unidad", "Unidad")
    comp_sel    = st.selectbox("🔬 Selecciona el componente a analizar:",
                               componentes, key="comp_sel")

    # Preparar datos del componente
    df_c = df_datos[[col_uid, comp_sel]].dropna().copy()
    df_c.columns = ["Unidad", "Valor"]
    df_c["Valor"] = pd.to_numeric(df_c["Valor"], errors="coerce")
    df_c.dropna(inplace=True)

    if len(df_c) < 4:
        st.error("Datos insuficientes para el análisis (mínimo 4 observaciones).")
        st.stop()

    r = analizar_componente(df_c, comp_sel, alpha, u_objetivo if usar_u_obj else None, u_obj_tipo)

    st.markdown(f"## 📊 Resultados: **{comp_sel}**")
    st.markdown(f"Diseño: **{r['n']} unidades** × **{r['m_eff']:.0f} réplicas** "
                f"({'balanceado' if r['balanced'] else 'desbalanceado'}) = **{len(df_c)} observaciones** "
                f"| Media global: **{r['grand_mean']:.5f}**")

    # ── Hipótesis ─────────────────────────────────────────────
    with st.expander("📐 Hipótesis planteadas", expanded=True):
        st.markdown(f"""
<div class="warn-box">
<b>H₀ (hipótesis nula):</b> Las medias de las {r['n']} unidades del lote son estadísticamente
iguales. No existe heterogeneidad significativa entre unidades para <i>{comp_sel}</i>.<br>
<i>α₁ = α₂ = ... = α_{r['n']} = 0</i><br><br>
<b>H₁ (hipótesis alternativa):</b> Al menos una unidad difiere significativamente de las demás.
Existe heterogeneidad en el lote para <i>{comp_sel}</i>.<br>
<b>Nivel de significancia:</b> α = {alpha} | <b>Regla de rechazo:</b> F_calc > F({r['gl_entre']}, {r['gl_res']}, {1-alpha:.2f}) = {r['F_crit']:.4f}
</div>""", unsafe_allow_html=True)

    # ── Decisión ──────────────────────────────────────────────
    if r["heterogeneo"]:
        st.markdown(
            f'<div class="err-box">⚠️ LOTE HETEROGÉNEO para {comp_sel} — '
            f'F({r["F_calc"]:.4f}) > F_crit({r["F_crit"]:.4f}) | p = {r["p_valor"]:.5f} ≤ α={alpha}<br>'
            f'Se rechaza H₀. Existe variabilidad significativa entre unidades.</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="ok-box">✅ LOTE HOMOGÉNEO para {comp_sel} — '
            f'F({r["F_calc"]:.4f}) ≤ F_crit({r["F_crit"]:.4f}) | p = {r["p_valor"]:.5f} > α={alpha}<br>'
            f'No se rechaza H₀. No hay evidencia de heterogeneidad significativa.</div>',
            unsafe_allow_html=True)

    # ── Métricas ──────────────────────────────────────────────
    mc = st.columns(5)
    mc[0].metric("F calculado",  f"{r['F_calc']:.4f}")
    mc[1].metric(f"F crítico (α={alpha})", f"{r['F_crit']:.4f}")
    mc[2].metric("p-valor",      f"{r['p_valor']:.5f}")
    mc[3].metric("u_hom",        f"{r['u_hom']:.6f}")
    mc[4].metric("u_hom DER%",   f"{r['u_hom']/r['grand_mean']*100:.4f}%")

    # ── Comparación u_hom vs u_objetivo ───────────────────────
    if r["u_comp"] is not None:
        estado_u, icono_u, ratio_u = r["u_comp"]
        color_u = {"despreciable":"ok-box","aceptable":"warn-box","inaceptable":"err-box"}[estado_u]
        st.markdown(f"""
<div class="{color_u}">
{icono_u} <b>Comparación con incertidumbre objetivo:</b><br>
u_hom = {r['u_hom']:.6f} | u_objetivo ({u_obj_tipo}) = {r['u_obj_abs']:.6f} |
Criterio (u_hom / u_obj) = <b>{ratio_u:.4f}</b><br>
→ La contribución de homogeneidad es <b>{estado_u.upper()}</b>
{"(u_hom < u_obj/3: puede omitirse de la incertidumbre combinada)" if estado_u=="despreciable"
 else "(u_hom < u_obj: debe propagarse en u_c)" if estado_u=="aceptable"
 else "(u_hom ≥ u_obj: el lote NO es apto para el uso previsto — revisar proceso de llenado)"}
</div>""", unsafe_allow_html=True)

    # ── Tabla ANOVA ───────────────────────────────────────────
    st.markdown('<p class="section-hdr">Tabla ANOVA</p>', unsafe_allow_html=True)
    anova_df = pd.DataFrame({
        "Fuente":              ["Entre unidades","Residual (dentro)","Total"],
        "Suma de Cuadrados":   [f"{r['SS_entre']:.6f}", f"{r['SS_res']:.6f}", f"{r['SS_entre']+r['SS_res']:.6f}"],
        "Grados de libertad":  [r['gl_entre'], r['gl_res'], r['gl_entre']+r['gl_res']],
        "Cuadrado Medio":      [f"{r['CM_entre']:.6f}", f"{r['CM_res']:.6f}", "—"],
        "F calculado":         [f"{r['F_calc']:.4f}", "—", "—"],
        f"F crítico (α={alpha})":[f"{r['F_crit']:.4f}", "—", "—"],
        "p-valor":             [f"{r['p_valor']:.6f}", "—", "—"],
        "Decisión":            [("Rechaza H₀ ⚠️" if r['heterogeneo'] else "No rechaza H₀ ✅"), "—", "—"],
    })
    st.dataframe(anova_df, hide_index=True, use_container_width=True)

    # ── Incertidumbre por homogeneidad ────────────────────────
    st.markdown('<p class="section-hdr">Incertidumbre por Homogeneidad — ISO 17034 §9.4</p>', unsafe_allow_html=True)
    ui1, ui2, ui3, ui4 = st.columns(4)
    ui1.metric("s²_bb", f"{r['s_bb_sq']:.8f}")
    ui2.metric("u_hom (abs)", f"{r['u_hom']:.6f}")
    ui3.metric("u_hom (DER%)", f"{r['u_hom']/r['grand_mean']*100:.4f}%")
    ui4.metric("Método", r['u_metodo'].split("→")[0].strip())
    st.markdown(f'<div class="interp">📌 <b>Fórmula aplicada:</b> {r["u_metodo"]}</div>', unsafe_allow_html=True)

    # ── Interpretación guiada ─────────────────────────────────
    with st.expander("📝 Interpretación completa del resultado", expanded=False):
        if not r['heterogeneo']:
            interp = f"""
El estadístico F calculado ({r['F_calc']:.4f}) es menor que el valor crítico F({r['gl_entre']},{r['gl_res']},
{1-alpha:.2f}) = {r['F_crit']:.4f}, con un p-valor de {r['p_valor']:.5f} > α={alpha}.
Por tanto, **no se rechaza H₀**: no existe evidencia estadística de que las unidades del lote
difieran significativamente entre sí para el componente **{comp_sel}**.

Dado que s²_bb = (CM_entre − CM_res)/m ≤ 0, se aplica la estimación conservadora de u_hom:
**u_hom = {r['u_hom']:.6f}** (DER = {r['u_hom']/r['grand_mean']*100:.4f}%).

Este valor debe incorporarse a la incertidumbre estándar combinada del valor de propiedad
del material de referencia: **u_c = √(u_caract² + u_hom² + u_estab²)**.
"""
        else:
            interp = f"""
El estadístico F calculado ({r['F_calc']:.4f}) supera el valor crítico F({r['gl_entre']},{r['gl_res']},
{1-alpha:.2f}) = {r['F_crit']:.4f}, con un p-valor de {r['p_valor']:.5f} ≤ α={alpha}.
Se **rechaza H₀**: existe heterogeneidad significativa entre unidades para **{comp_sel}**.

Se cuantifica la varianza entre unidades: s²_bb = {r['s_bb_sq']:.8f},
y la incertidumbre de homogeneidad: **u_hom = {r['u_hom']:.6f}** (DER = {r['u_hom']/r['grand_mean']*100:.4f}%).

Se recomienda **investigar las causas** de la heterogeneidad (proceso de llenado, estabilidad
del analito durante el llenado, contaminación cruzada) antes de certificar el material.
"""
        st.markdown(interp)

    # ── Gráficos principales ──────────────────────────────────
    st.markdown('<p class="section-hdr">Gráficos del análisis</p>', unsafe_allow_html=True)
    colors = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b",
              "#e377c2","#7f7f7f","#bcbd22","#17becf","#aec7e8","#ffbb78"]
    g1, g2 = st.columns(2)

    # Scatter réplicas + medias
    fig_s = go.Figure()
    for i, u in enumerate(r['unidades']):
        vals = df_c[df_c["Unidad"]==u]["Valor"].values
        c = colors[i % len(colors)]
        fig_s.add_trace(go.Scatter(x=[str(u)]*len(vals), y=vals, mode="markers",
            marker=dict(size=10, opacity=0.5, color=c), showlegend=False))
        fig_s.add_trace(go.Scatter(x=[str(u)], y=[r['unit_means'][u]], mode="markers",
            marker=dict(size=14, symbol="diamond", color=c, line=dict(width=2, color="white")),
            showlegend=False))
    fig_s.add_hline(y=r['grand_mean'], line_dash="dash", line_color="gray",
                    annotation_text=f"x̄={r['grand_mean']:.4f}", annotation_position="top right")
    fig_s.update_layout(title=f"{comp_sel}: réplicas por unidad",
                        xaxis_title="Unidad", yaxis_title="Valor", height=380,
                        margin=dict(t=50,b=50,l=60,r=20))
    g1.plotly_chart(fig_s, use_container_width=True)

    # Barras medias ± u_hom
    fig_b = go.Figure()
    for i, u in enumerate(r['unidades']):
        fig_b.add_trace(go.Bar(x=[str(u)], y=[r['unit_means'][u]],
            marker_color=colors[i%len(colors)], showlegend=False,
            error_y=dict(type="constant", value=r['u_hom'], visible=True,
                         color="#888", thickness=1.5, width=8)))
    fig_b.add_hline(y=r['grand_mean'], line_dash="dot", line_color="gray",
                    annotation_text=f"x̄={r['grand_mean']:.4f}", annotation_position="top right")
    y_rng = max(abs(m - r['grand_mean']) for m in r['unit_means'].values)
    fig_b.update_layout(title=f"{comp_sel}: medias ± u_hom ({r['u_hom']:.5f})",
                        xaxis_title="Unidad", yaxis_title="Media",
                        yaxis=dict(range=[r['grand_mean']-max(y_rng*2,r['u_hom']*6),
                                          r['grand_mean']+max(y_rng*2,r['u_hom']*6)]),
                        height=380, margin=dict(t=50,b=50,l=70,r=20))
    g2.plotly_chart(fig_b, use_container_width=True)

    # ── ANÁLISIS DE RESIDUALES ────────────────────────────────
    st.markdown('<p class="section-hdr">Análisis de Residuales del Modelo</p>', unsafe_allow_html=True)

    # Pruebas
    pr1, pr2 = st.columns(2)
    sw_ok = r['sw_p'] > alpha if not np.isnan(r['sw_p']) else None
    bt_ok = r['bt_p'] > alpha if not np.isnan(r['bt_p']) else None

    with pr1:
        st.markdown("**Prueba de Shapiro-Wilk** (normalidad de residuales)")
        css = "ok-box" if sw_ok else "err-box"
        msg = "✅ Residuales normales (no se rechaza H₀)" if sw_ok else "⚠️ No normalidad (se rechaza H₀)"
        st.markdown(f'<div class="{css}">W = {r["sw_stat"]:.5f} | p = {r["sw_p"]:.5f} | {msg}</div>',
                    unsafe_allow_html=True)
    with pr2:
        st.markdown("**Prueba de Bartlett** (homogeneidad de varianzas)")
        css2 = "ok-box" if bt_ok else "err-box"
        msg2 = "✅ Varianzas homogéneas (no se rechaza H₀)" if bt_ok else "⚠️ Varianzas heterogéneas (se rechaza H₀)"
        st.markdown(f'<div class="{css2}">χ² = {r["bt_stat"]:.4f} | p = {r["bt_p"]:.5f} | {msg2}</div>',
                    unsafe_allow_html=True)

    # Gráficos de residuales
    rg1, rg2 = st.columns(2)

    # Residuales vs valores ajustados
    fig_rv = go.Figure()
    fig_rv.add_trace(go.Scatter(x=r['fitted'], y=r['residuales'], mode="markers",
        marker=dict(size=9, color="#27ae60", opacity=0.7), showlegend=False))
    fig_rv.add_hline(y=0, line_dash="dash", line_color="red", line_width=1.5)
    fig_rv.update_layout(title="Residuales vs valores ajustados",
                         xaxis_title="Valor ajustado (media unidad)",
                         yaxis_title="Residual", height=340,
                         margin=dict(t=50,b=50,l=60,r=20))
    rg1.plotly_chart(fig_rv, use_container_width=True)

    # Q-Q plot
    (osm, osr), (slope, intercept, _) = stats.probplot(r['residuales'])
    fig_qq = go.Figure()
    fig_qq.add_trace(go.Scatter(x=osm, y=osr, mode="markers",
        marker=dict(size=9, color="#27ae60", opacity=0.8), name="Residuales"))
    x_line = np.array([min(osm), max(osm)])
    fig_qq.add_trace(go.Scatter(x=x_line, y=slope*x_line+intercept,
        mode="lines", line=dict(color="red", dash="dash", width=2), name="Normal teórica"))
    fig_qq.update_layout(title="Gráfico Q-Q Normal de residuales",
                         xaxis_title="Cuantiles teóricos",
                         yaxis_title="Cuantiles observados",
                         height=340, margin=dict(t=50,b=50,l=60,r=20),
                         legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"))
    rg2.plotly_chart(fig_qq, use_container_width=True)

    # Histograma de residuales
    fig_h = go.Figure()
    fig_h.add_trace(go.Histogram(x=r['residuales'], nbinsx=min(15, len(r['residuales'])//2+1),
        marker_color="#8e44ad", opacity=0.75, name="Residuales"))
    fig_h.update_layout(title="Distribución de residuales",
                        xaxis_title="Residual", yaxis_title="Frecuencia",
                        height=300, margin=dict(t=50,b=50,l=60,r=20), showlegend=False)
    st.plotly_chart(fig_h, use_container_width=True)

    # ── Exportar ──────────────────────────────────────────────
    st.markdown('<p class="section-hdr">Exportar resultados</p>', unsafe_allow_html=True)
    buf_xl = io.BytesIO()
    resumen_df = pd.DataFrame({
        "Parámetro": ["Componente","N unidades","Réplicas/unidad","Media global",
                      "CM_entre","CM_res","F_calc",f"F_crit_alpha{alpha}","p_valor",
                      "Decisión","s_bb_cuadrado","u_hom","u_hom_DER_pct",
                      "Shapiro-Wilk W","Shapiro-Wilk p","Bartlett stat","Bartlett p"],
        "Valor": [comp_sel, r['n'], round(r['m_eff'],2), round(r['grand_mean'],8),
                  round(r['CM_entre'],8), round(r['CM_res'],8),
                  round(r['F_calc'],6), round(r['F_crit'],6), round(r['p_valor'],6),
                  "HETEROGENEO" if r['heterogeneo'] else "HOMOGENEO",
                  round(r['s_bb_sq'],10), round(r['u_hom'],8),
                  round(r['u_hom']/r['grand_mean']*100,6),
                  round(r['sw_stat'],6), round(r['sw_p'],6),
                  round(r['bt_stat'],4), round(r['bt_p'],6)]
    })
    tbl_u = pd.DataFrame({
        "Unidad": [str(u) for u in r['unidades']],
        "N_rep":  [int(r['rep_counts'][u]) for u in r['unidades']],
        "Media":  [round(r['unit_means'][u],6) for u in r['unidades']],
        "Desv_std": [round(df_c[df_c["Unidad"]==u]["Valor"].std(ddof=1),6) for u in r['unidades']],
    })
    res_df = pd.DataFrame({"Unidad": df_c["Unidad"].values,
                           "Valor ajustado": r['fitted'],
                           "Residual": r['residuales']})
    with pd.ExcelWriter(buf_xl, engine="openpyxl") as w:
        resumen_df.to_excel(w, sheet_name="Resumen",     index=False)
        anova_df.to_excel(w,   sheet_name="ANOVA",       index=False)
        tbl_u.to_excel(w,      sheet_name="Por_unidad",  index=False)
        res_df.to_excel(w,     sheet_name="Residuales",  index=False)
        df_c.to_excel(w,       sheet_name="Datos_brutos",index=False)
    st.download_button(f"⬇️ Descargar reporte completo — {comp_sel} (.xlsx)",
                       data=buf_xl.getvalue(),
                       file_name=f"homogeneidad_{comp_sel.replace(' ','_')}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ════════════════════════════════════════════════════════════
#  PÁGINA 4 — RESUMEN GENERAL (todos los componentes)
# ════════════════════════════════════════════════════════════
elif pagina == "📋 Resumen General":
    if st.session_state["df_datos"] is None:
        st.warning("⚠️ Primero carga tus datos en la página **📁 Ingreso de Datos**.")
        st.stop()

    st.markdown("## 📋 Resumen General — Todos los Componentes")
    df_datos    = st.session_state["df_datos"]
    componentes = st.session_state["componentes"]
    col_uid     = st.session_state.get("col_unidad","Unidad")

    with st.spinner(f"Analizando {len(componentes)} componente(s)..."):
        filas = []
        for comp in componentes:
            df_c = df_datos[[col_uid, comp]].dropna().copy()
            df_c.columns = ["Unidad","Valor"]
            df_c["Valor"] = pd.to_numeric(df_c["Valor"], errors="coerce")
            df_c.dropna(inplace=True)
            if len(df_c) < 4:
                continue
            r = analizar_componente(df_c, comp, alpha,
                                    u_objetivo if usar_u_obj else None, u_obj_tipo)
            fila = {
                "Componente":    comp,
                "N unidades":    r['n'],
                "Réplicas":      round(r['m_eff'],1),
                "Media global":  round(r['grand_mean'],5),
                "F calculado":   round(r['F_calc'],4),
                f"F crit (α={alpha})": round(r['F_crit'],4),
                "p-valor":       round(r['p_valor'],5),
                "Decisión":      "⚠️ HETEROGÉNEO" if r['heterogeneo'] else "✅ HOMOGÉNEO",
                "u_hom":         round(r['u_hom'],6),
                "u_hom DER%":    round(r['u_hom']/r['grand_mean']*100,4),
                "Normalidad (SW p)": round(r['sw_p'],4) if not np.isnan(r['sw_p']) else "—",
                "Homoced. (Bart p)": round(r['bt_p'],4) if not np.isnan(r['bt_p']) else "—",
            }
            if r['u_comp']:
                fila["u_hom vs u_obj"] = r['u_comp'][1] + " " + r['u_comp'][0]
            filas.append(fila)

    df_res = pd.DataFrame(filas)
    st.dataframe(df_res, hide_index=True, use_container_width=True)

    # Gráfico de u_hom por componente
    if len(df_res) > 0:
        fig_sum = go.Figure()
        colors_s = ["#27ae60" if "HOMOG" in d else "#e74c3c" for d in df_res["Decisión"]]
        fig_sum.add_trace(go.Bar(x=df_res["Componente"], y=df_res["u_hom DER%"],
            marker_color=colors_s, showlegend=False,
            text=[f"{v:.3f}%" for v in df_res["u_hom DER%"]], textposition="outside"))
        if usar_u_obj and u_objetivo is not None:
            u_obj_der = u_objetivo if "relativa" in u_obj_tipo else None
            if u_obj_der:
                fig_sum.add_hline(y=u_obj_der, line_dash="dash", line_color="orange",
                                  annotation_text=f"u_obj={u_obj_der:.2f}%")
                fig_sum.add_hline(y=u_obj_der/3, line_dash="dot", line_color="green",
                                  annotation_text=f"u_obj/3={u_obj_der/3:.2f}%")
        fig_sum.update_layout(title="u_hom DER% por componente (verde=homogéneo, rojo=heterogéneo)",
                              xaxis_title="Componente", yaxis_title="u_hom DER%",
                              height=420, margin=dict(t=60,b=80,l=60,r=20))
        fig_sum.update_xaxes(tickangle=45)
        st.plotly_chart(fig_sum, use_container_width=True)

    # Exportar resumen
    buf_s = io.BytesIO()
    df_res.to_excel(buf_s, index=False)
    st.download_button("⬇️ Descargar resumen general (.xlsx)",
                       data=buf_s.getvalue(),
                       file_name="resumen_homogeneidad_todos_componentes.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Footer
st.markdown("---")
st.caption("ICA – Área IIAD · LANIA | Evaluación de homogeneidad de MR e ítems de EA | ISO 17034:2017 §9.4 | v2.2")
