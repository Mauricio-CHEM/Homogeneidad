# 🧪 Evaluación de Homogeneidad — ISO 17034:2017 §9.4

> Aplicativo web desarrollado con **Streamlit** para evaluar la homogeneidad de lotes de materiales de referencia mediante ANOVA de una vía, conforme a los requisitos del numeral 9.4 de la norma **ISO 17034:2017**.

**Instituto Colombiano Agropecuario (ICA) — Subgerencia de Análisis y Diagnóstico**

---

## 📋 Contenido

- [Descripción](#-descripción)
- [Fundamento estadístico](#-fundamento-estadístico)
- [Instalación local](#-instalación-local)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Uso de la aplicación](#-uso-de-la-aplicación)
- [Formato del archivo Excel](#-formato-del-archivo-excel)
- [Interpretación de resultados](#-interpretación-de-resultados)
- [Despliegue en la nube](#-despliegue-en-la-nube-streamlit-community-cloud)
- [Referencias normativas](#-referencias-normativas)

---

## 📌 Descripción

Este aplicativo permite a los profesionales del laboratorio evaluar la **homogeneidad entre unidades** de un lote de material de referencia sin necesidad de interactuar con código. El usuario puede:

- Cargar sus datos directamente desde un archivo **Excel (.xlsx)**
- Ingresar datos **manualmente** mediante una tabla interactiva
- Obtener la **tabla ANOVA**, la decisión estadística y la **incertidumbre por homogeneidad (u_hom)**
- Visualizar los resultados en **gráficos interactivos**
- **Exportar** el reporte completo en `.csv` o `.xlsx`

---

## 📐 Fundamento Estadístico

El análisis se basa en el **ANOVA de una vía** tal como se describe en:
- ISO 17034:2017 §9.4 — Estudio de homogeneidad
- ISO Guide 35:2017 §9.3
- IUPAC Technical Report — Production and certification of reference materials

### Hipótesis

| Hipótesis | Descripción |
|-----------|-------------|
| **H₀** | No existe diferencia significativa entre las medias de las unidades (lote homogéneo) |
| **H₁** | Existe diferencia significativa entre al menos dos unidades (lote heterogéneo) |

### Estadístico F

$$F = \frac{CM_{entre}}{CM_{residual}}$$

| Fuente | Suma de Cuadrados | gl | Cuadrado Medio |
|--------|-------------------|-----|----------------|
| Entre unidades | $SS_{entre} = m \sum_{i=1}^{n}(\bar{x}_i - \bar{x})^2$ | $n-1$ | $CM_{entre} = SS_{entre}/(n-1)$ |
| Residual | $SS_{res} = \sum_{i=1}^{n}\sum_{j=1}^{m}(x_{ij}-\bar{x}_i)^2$ | $n(m-1)$ | $CM_{res} = SS_{res}/[n(m-1)]$ |

### Incertidumbre por homogeneidad (u_hom)

Se aplica lógica de decisión automática:

```
Si s²bb = (CM_entre − CM_res) / m  > 0:
    u_hom = √(s²bb)                         ← varianza real entre unidades

Si s²bb ≤ 0  (CM_entre ≤ CM_res):
    u_hom = √(CM_res / m)                   ← estimación conservadora
```

Para diseños **desbalanceados** (diferente número de réplicas por unidad), se usa el número efectivo de réplicas $\tilde{m}$:

$$\tilde{m} = \frac{N^2 - \sum n_i^2}{(n-1)\cdot N}$$

---

## 💻 Instalación Local

### Requisitos previos
- Python 3.9 o superior
- pip

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/<tu-usuario>/homogeneidad-iso17034.git
cd homogeneidad-iso17034

# 2. (Opcional) Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Lanzar la aplicación
streamlit run app.py
```

La app se abrirá automáticamente en: **http://localhost:8501**

---

## 📁 Estructura del Proyecto

```
homogeneidad-iso17034/
│
├── app.py                        # Aplicativo principal Streamlit
├── requirements.txt              # Dependencias Python
├── README.md                     # Este archivo
│
└── ejemplo/
    └── plantilla_homogeneidad.xlsx   # Plantilla Excel de ejemplo
```

---

## 🖥️ Uso de la Aplicación

### 1. Panel lateral (Sidebar)

| Control | Descripción |
|---------|-------------|
| **Nivel de significancia (α)** | Selecciona 0.01, 0.05 o 0.10 |
| **Nombre columna Unidad** | Nombre exacto de la columna de unidades en tu Excel |
| **Nombre columna Medicion** | Nombre exacto de la columna de mediciones en tu Excel |
| **Descargar plantilla** | Descarga una plantilla Excel con el formato requerido |

### 2. Pestaña "Cargar Excel"

1. Haz clic en **"Browse files"** y selecciona tu archivo `.xlsx` o `.xls`
2. Verifica que la vista previa muestre tus datos correctamente
3. El análisis se ejecuta automáticamente al cargar el archivo

### 3. Pestaña "Ingresar manualmente"

1. Define el **número de unidades** y **réplicas por unidad**
2. Completa la tabla haciendo **doble clic** en cada celda
3. Haz clic en **"▶ Usar datos manuales"** para ejecutar el análisis

### 4. Resultados

- **Tarjeta de decisión**: verde (✅ Homogéneo) o rojo (⚠️ Heterogéneo)
- **Métricas rápidas**: N unidades, réplicas, media global, u_hom, DER%
- **Tabla ANOVA completa**
- **Incertidumbre u_hom** con método aplicado
- **Gráficos interactivos**: réplicas por unidad y medias ± u_hom
- **Botones de exportación**: `.csv` y `.xlsx` con reporte completo

---

## 📊 Formato del Archivo Excel

El archivo Excel debe contener **mínimo dos columnas**:

| Unidad | Medicion |
|--------|----------|
| 1      | 21.0     |
| 1      | 21.5     |
| 1      | 20.8     |
| 2      | 20.2     |
| 2      | 20.0     |
| 2      | 21.1     |
| ...    | ...      |

> **Notas:**
> - Los nombres de columna pueden personalizarse en la barra lateral
> - Se admiten diseños **balanceados** (igual número de réplicas por unidad) y **desbalanceados**
> - El número mínimo recomendado es **10 unidades con 3 réplicas** cada una (ISO 17034)
> - Las celdas vacías se ignoran automáticamente

---

## 📈 Interpretación de Resultados

### Decisión estadística

| Condición | Conclusión |
|-----------|------------|
| `F_calc ≤ F_crit` y `p > α` | ✅ **Lote homogéneo** — u_hom se propaga como componente de incertidumbre |
| `F_calc > F_crit` y `p ≤ α` | ⚠️ **Lote heterogéneo** — investigar causas; considerar rechazo o re-llenado |

### Uso de u_hom en la incertidumbre combinada

Cuando el lote es homogéneo, `u_hom` se incorpora a la incertidumbre estándar combinada del valor de propiedad del material de referencia:

$$u_c = \sqrt{u_{caract}^2 + u_{hom}^2 + u_{estab}^2}$$

---

## ☁️ Despliegue en la Nube (Streamlit Community Cloud)

Puedes publicar la aplicación **de forma gratuita** sin que los usuarios necesiten instalar nada:

1. Sube el repositorio a **GitHub** (debe ser público o con acceso configurado)
2. Ve a [share.streamlit.io](https://share.streamlit.io) e inicia sesión con tu cuenta de GitHub
3. Haz clic en **"New app"**
4. Selecciona el repositorio, rama (`main`) y el archivo principal (`app.py`)
5. Haz clic en **"Deploy"** — en pocos minutos tendrás una URL pública

```
https://<tu-usuario>-homogeneidad-iso17034-app-xxxx.streamlit.app
```

---

## 🔧 Dependencias

| Librería | Versión mínima | Uso |
|----------|---------------|-----|
| `streamlit` | 1.32.0 | Interfaz web |
| `pandas` | 2.0.0 | Manipulación de datos |
| `numpy` | 1.24.0 | Cálculos numéricos |
| `scipy` | 1.11.0 | Distribución F y estadísticos |
| `plotly` | 5.18.0 | Gráficos interactivos |
| `openpyxl` | 3.1.0 | Lectura/escritura de Excel |

---

## 📚 Referencias Normativas

- **ISO 17034:2017** — General requirements for the competence of reference material producers. §9.4 Homogeneity study.
- **ISO Guide 35:2017** — Reference materials — Guidance for characterization and assessment of homogeneity and stability.
- **ISO 13528:2022** — Statistical methods for use in proficiency testing by interlaboratory comparison.
- **EURACHEM/CITAC CG 4** — Quantifying Uncertainty in Analytical Measurement (QUAM:2012).
- **IUPAC Technical Report (2006)** — Metrological and Quality Concepts in Analytical Chemistry.

---

## 👥 Autoría y Contexto

Desarrollado en el marco del proyecto **ARCAL RLA/5/091** y el convenio **ICA–INM** bajo **CONPES 4052**, para el establecimiento de áreas de referencia del ICA como:

- Productor de Materiales de Referencia (ISO 17034)
- Proveedor de Ensayos de Aptitud (ISO/IEC 17043)

**Instituto Colombiano Agropecuario — ICA**
Subgerencia de Análisis y Diagnóstico (SAD)
Bogotá D.C., Colombia

---

## 📄 Licencia

Uso interno ICA. Para adaptaciones o redistribución, consultar con la Subgerencia de Análisis y Diagnóstico.
