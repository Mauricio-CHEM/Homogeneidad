# 🧪 Evaluación de Homogeneidad de MR e Ítems de Ensayo de Aptitud

> **Área IIAD · LANIA — Instituto Colombiano Agropecuario (ICA)**
> Subgerencia de Análisis y Diagnóstico

Aplicativo web desarrollado con **Streamlit** para evaluar la homogeneidad de lotes de materiales de referencia e ítems de ensayo de aptitud mediante ANOVA de una vía, conforme a **ISO 17034:2017 §9.4**.

🔗 **App en producción:** [iiad-homogeneidad-v1.streamlit.app](https://iiad-homogeneidad-v1.streamlit.app/)

---

## 📋 Tabla de contenido

- [Descripción](#-descripción)
- [Fundamento estadístico](#-fundamento-estadístico)
- [Instalación local](#-instalación-local)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Páginas del aplicativo](#-páginas-del-aplicativo)
- [Formato del archivo Excel](#-formato-del-archivo-excel)
- [Interpretación de resultados](#-interpretación-de-resultados)
- [Logo institucional](#-logo-institucional)
- [Despliegue en la nube](#-despliegue-en-la-nube)
- [Historial de versiones](#-historial-de-versiones)
- [Referencias normativas](#-referencias-normativas)

---

## 📌 Descripción

Este aplicativo permite a los profesionales del laboratorio evaluar la **homogeneidad entre unidades** de un lote sin necesidad de interactuar con código. Soporta análisis simultáneo de hasta **37 componentes/moléculas** en un solo archivo Excel.

**Capacidades principales:**
- Carga de datos desde **Excel multi-componente** o ingreso manual en tabla interactiva
- **ANOVA de una vía** con tabla completa, decisión estadística e interpretación guiada
- Cálculo de **incertidumbre por homogeneidad (u_hom)** conforme a ISO 17034 §9.4
- Comparación automática de **u_hom vs incertidumbre objetivo** con semáforo de aptitud
- **Análisis de residuales** completo: Shapiro-Wilk, Bartlett, Q-Q, scatter de residuales
- **Resumen general** de todos los componentes en una sola tabla con gráfico comparativo
- Exportación del reporte en **`.csv`** y **`.xlsx`** (5 hojas: Resumen, ANOVA, Por unidad, Residuales, Datos brutos)

---

## 📐 Fundamento Estadístico

El análisis se basa en el **ANOVA de una vía** (ISO 17034:2017 §9.4, ISO Guide 35:2017 §9.3):

### Hipótesis

| | Descripción |
|---|---|
| **H₀** | Las medias de todas las unidades son iguales — lote homogéneo |
| **H₁** | Al menos una unidad difiere significativamente — lote heterogéneo |

### Tabla ANOVA

| Fuente | SC | gl | CM |
|--------|-----|-----|-----|
| Entre unidades | m·Σ(x̄ᵢ − x̄)² | n−1 | CM_entre |
| Residual | ΣΣ(xᵢⱼ − x̄ᵢ)² | n(m−1) | CM_res |

**Estadístico:** F = CM_entre / CM_res; se rechaza H₀ si F > F(n−1, n(m−1), 1−α)

### Incertidumbre por homogeneidad

```
s²bb = (CM_entre − CM_res) / m

Si s²bb > 0 → u_hom = √(s²bb)                    [varianza real entre unidades]
Si s²bb ≤ 0 → u_hom = √(CM_res / m)               [estimación conservadora]
```

Para diseños desbalanceados se usa el número efectivo de réplicas m̃ = (N² − Σnᵢ²) / [(n−1)·N]

### Criterio de aptitud (ISO Guide 35)

| Condición | Estado |
|-----------|--------|
| u_hom < u_obj / 3 | ✅ Contribución despreciable |
| u_hom < u_obj | ⚠️ Aceptable — debe propagarse en u_c |
| u_hom ≥ u_obj | ❌ Lote inaceptable para el uso previsto |

---

## 💻 Instalación Local

```bash
# 1. Clonar el repositorio
git clone https://github.com/<tu-usuario>/homogeneidad-iso17034.git
cd homogeneidad-iso17034

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
streamlit run app.py
```

Abre en el navegador: **http://localhost:8501**

---

## 📁 Estructura del Proyecto

```
homogeneidad-iso17034/
│
├── app.py                              # Aplicativo principal Streamlit (v2.3)
├── requirements.txt                    # Dependencias Python
├── README.md                           # Este archivo
│
├── assets/
│   └── logo_ica.png                    # Logo institucional ICA (PNG)
│
└── ejemplo/
    └── plantilla_homogeneidad_multi.xlsx  # Plantilla Excel multi-componente
```

> **Nota:** Si `assets/logo_ica.png` no existe, la app muestra un emoji de fallback y continúa funcionando normalmente.

---

## 🖥️ Páginas del Aplicativo

### 🏠 Inicio e Instrucciones
Pantalla de bienvenida con fundamento teórico, diseño experimental recomendado, hipótesis del ANOVA, criterios de interpretación, supuestos del modelo y guía de uso paso a paso.

### 📁 Ingreso de Datos
Dos modos de entrada:

| Modo | Descripción |
|------|-------------|
| **Cargar Excel** | Sube archivo `.xlsx`/`.xls` con columna `Unidad` + columnas por componente |
| **Ingresar manualmente** | Define unidades, réplicas y componentes; llena tabla interactiva en pantalla |

### 📊 Resultados por Componente
Selector desplegable para elegir el componente a analizar. Muestra:
- Hipótesis formalizadas con valores del experimento
- Tarjeta de decisión (verde/rojo)
- Tabla ANOVA completa
- u_hom con método aplicado e interpretación guiada
- Comparación u_hom vs u_objetivo (si está configurado en el sidebar)
- Análisis de residuales: Shapiro-Wilk, Bartlett, Q-Q, scatter, histograma
- Botón de exportación individual por componente

### 📋 Resumen General
Tabla consolidada con todos los componentes: F, F_crit, p-valor, decisión, u_hom, DER%, resultados de pruebas de residuales. Gráfico de barras comparativo con líneas de referencia u_obj y u_obj/3. Exportación a Excel.

---

## 📊 Formato del Archivo Excel

```
Unidad | Clorpirifos | Cipermetrina | Malatión | ... (hasta 37 columnas)
  1    |    21.30    |    15.20     |   8.10   |
  1    |    21.10    |    15.40     |   8.30   |
  1    |    21.50    |    15.10     |   8.00   |
  2    |    20.80    |    14.90     |   8.20   |
  ...
```

- Cada **fila** = una réplica independiente
- Cada **columna** (excepto `Unidad`) = un componente/analito
- El nombre de la columna identificadora puede cambiarse en el sidebar
- Se admiten diseños **balanceados y desbalanceados**
- Mínimo recomendado: **10 unidades × 3 réplicas** (ISO 17034)

---

## 📈 Interpretación de Resultados

### Decisión estadística

| Condición | Conclusión | Acción recomendada |
|-----------|------------|--------------------|
| F ≤ F_crit (p > α) | ✅ Homogéneo | Propagar u_hom en u_c del certificado |
| F > F_crit (p ≤ α) | ⚠️ Heterogéneo | Investigar proceso de llenado; considerar rechazo del lote |

### Supuestos del modelo (análisis de residuales)

| Prueba | H₀ | Supuesto cumplido si |
|--------|-----|----------------------|
| Shapiro-Wilk | Residuales normales | p > α |
| Bartlett | Varianzas iguales entre unidades | p > α |
| Q-Q plot | Puntos sobre la diagonal | Visualmente alineados |
| Residuales vs ajustados | Sin patrón sistemático | Dispersión aleatoria en torno a 0 |

### Incorporación a la incertidumbre combinada

```
u_c = √(u_caract² + u_hom² + u_estab²)
U   = k · u_c    (k=2 para ~95% de confianza)
```

---

## 🖼️ Logo Institucional

1. Coloca el archivo PNG en `assets/logo_ica.png`
2. El logo aparece automáticamente en el banner superior y en el sidebar
3. Si el archivo no existe, la app usa un emoji como fallback sin errores

---

## ☁️ Despliegue en la Nube

1. Sube el repositorio a **GitHub** (público o privado con acceso)
2. Ve a [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Selecciona el repositorio, rama `main` y archivo `app.py`
4. Clic en **Deploy** → URL pública disponible en ~2 minutos

---

## 🔧 Dependencias

| Librería | Versión mínima | Uso |
|----------|---------------|-----|
| `streamlit` | 1.32.0 | Interfaz web |
| `pandas` | 2.0.0 | Manipulación de datos |
| `numpy` | 1.24.0 | Cálculos numéricos |
| `scipy` | 1.11.0 | Distribución F, Shapiro-Wilk, Bartlett |
| `plotly` | 5.18.0 | Gráficos interactivos |
| `openpyxl` | 3.1.0 | Lectura/escritura de Excel |

---

## 📝 Historial de Versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| v1.0 | Mar 2026 | Algoritmo ANOVA base en Python |
| v1.1 | Mar 2026 | Lectura desde Excel + gráficos Plotly |
| v2.0 | Mar 2026 | App Streamlit completa: multi-componente, residuales, u_objetivo, 4 páginas |
| v2.1 | Mar 2026 | Paleta verde institucional ICA + banner |
| v2.2 | Mar 2026 | Logo institucional PNG en banner y sidebar |
| v2.3 | Mar 2026 | Fix SyntaxError Python en f-string con backslash |

---

## 📚 Referencias Normativas

- **ISO 17034:2017** — General requirements for the competence of reference material producers. §9.4 Homogeneity study.
- **ISO Guide 35:2017** — Reference materials — Guidance for characterization and assessment of homogeneity and stability.
- **ISO 13528:2022** — Statistical methods for use in proficiency testing by interlaboratory comparison.
- **EURACHEM/CITAC CG 4** — Quantifying Uncertainty in Analytical Measurement (QUAM:2012).

---

## 👥 Contexto Institucional

Desarrollado en el marco del proyecto **ARCAL RLA/5/091** y el convenio **ICA–INM** bajo **CONPES 4052**, para el establecimiento de las áreas de referencia del ICA como Productor de Materiales de Referencia (ISO 17034) y Proveedor de Ensayos de Aptitud (ISO/IEC 17043).

**Instituto Colombiano Agropecuario — ICA**
Subgerencia de Análisis y Diagnóstico (SAD) · Área IIAD · LANIA
Bogotá D.C., Colombia

---

## 📄 Licencia

Uso interno ICA. Para adaptaciones o redistribución consultar con la Subgerencia de Análisis y Diagnóstico.
