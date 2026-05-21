# SmartRisk — Robo-Advisor Académico

Plataforma de simulación estocástica y asesoramiento financiero basada en Streamlit. Permite construir portafolios de inversión, simular su evolución mediante el Movimiento Browniano Geométrico (GBM), y evaluar métricas de riesgo como VaR, CVaR, Sharpe Ratio y Max Drawdown.

> **Nota:** Todas las simulaciones son proyecciones estadísticas con fines académicos. No constituyen asesoría financiera ni garantizan rendimientos futuros.

---

## Inicio Rápido

```bash
# 1. Crear entorno virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
streamlit run app.py
```

La aplicación abrirá automáticamente en `http://localhost:8501`.

> **Windows:** Los archivos JSON con emojis se leen con `encoding="utf-8"` de forma predeterminada. No requiere configuración adicional.

---

## Credenciales por Defecto

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| Administrador | `admin` | `Admin1234!` |

El usuario administrador se crea automáticamente en el primer inicio. Desde el panel admin puedes crear, editar y asignar roles a otros usuarios.

---

## Estructura del Proyecto

```
smartrisk/
├── app.py                        # Punto de entrada — configuración global + routing
├── requirements.txt              # Dependencias (streamlit, yfinance, numpy, scipy, ...)
├── .streamlit/
│   └── config.toml               # Tema visual y configuración del servidor
│
├── config/
│   ├── settings.py               # Constantes globales: rutas, defaults, límites
│   ├── assets.json               # Catálogo de 50+ activos (acciones, ETFs, bonos, REITs)
│   └── risk_profiles.json        # Perfiles de riesgo con emojis y descripciones
│
├── auth/
│   ├── auth_service.py           # Lógica de registro, login y validación de email
│   ├── login.py                  # UI de login y registro
│   ├── password_utils.py         # Hashing y verificación con bcrypt
│   └── session_manager.py        # Manejo de sesión via Streamlit session_state
│
├── database/
│   └── repositories.py           # CRUD completo sobre archivos JSON (usuarios, portafolios, simulaciones)
│
├── core/
│   ├── finance/
│   │   ├── monte_carlo.py        # Motor GBM multi-escenario con DCA corregido
│   │   ├── markowitz.py          # Optimización: Sharpe máximo, varianza mínima, frontera eficiente
│   │   └── metrics.py            # VaR, CVaR, Sharpe, Sortino, Calmar, Max Drawdown
│   ├── market/
│   │   └── downloader.py         # Descarga de datos históricos via yfinance + caché local
│   └── utils/                    # (vacío — validadores fueron eliminados por no usarse)
│
├── services/
│   ├── portfolio_service.py      # Orquesta descarga + optimización + construcción de cartera
│   ├── simulation_service.py     # Orquesta simulación Monte Carlo con métricas
│   ├── market_service.py         # Carga centralizada de catálogo de activos y perfiles de riesgo
│   └── user_service.py           # Operaciones CRUD sobre usuarios
│
├── ui/
│   ├── pages/
│   │   ├── dashboard.py          # Panel principal con resumen y onboarding
│   │   ├── risk_quiz.py          # Quiz de perfil de riesgo (5 preguntas)
│   │   ├── portfolio_builder.py  # Constructor de cartera con inputs numéricos
│   │   ├── simulator.py          # Simulador con parámetros ajustables + gráficos
│   │   ├── results.py            # Historial de simulaciones con exportación CSV
│   │   ├── admin_panel.py        # CRUD de usuarios y estadísticas globales
│   │   └── profile.py            # Edición de perfil y cambio de contraseña
│   ├── components/
│   │   ├── sidebar.py            # Barra lateral con navegación contextual
│   │   ├── charts.py             # Componentes Plotly: fan chart, distribución, frontera eficiente
│   │   └── metrics_cards.py      # Cards, alertas, tooltips y separadores
│   └── styles/
│       └── custom_css.py         # CSS personalizado con paleta de colores institucional
│
├── tests/
│   ├── test_monte_carlo.py       # 15+ tests unitarios para el motor GBM
│   ├── test_markowitz.py         # 12+ tests para optimización de portafolio
│   └── test_metrics.py           # 18+ tests para métricas de riesgo
│
├── data/                         # Directorios creados automáticamente en el primer inicio
│   ├── users.json                # (autogenerado)
│   ├── portfolios.json           # (autogenerado)
│   ├── simulations.json          # (autogenerado)
│   ├── risk_results.json         # (autogenerado)
│   ├── cache/                    # Caché de precios históricos (CSV)
│   └── exports/                  # Exportaciones descargadas por el usuario
│
└── debugging/
    └── GUIA_DEBUGGING.md         # Historial de bugs corregidos y mejoras implementadas
```

---

## Flujo de Trabajo del Usuario

```
Registro / Login
       │
       ▼
   ┌───────────────┐
   │   Dashboard   │  ← Resumen de portafolios, simulaciones y perfil de riesgo
   └───────┬───────┘
           │
     ┌─────▼──────┐
     │ Perfil de  │  ← Quiz interactivo de 5 preguntas
     │  Riesgo    │  → Clasificación: Conservador / Moderado / Agresivo
     └─────┬──────┘
           │
     ┌─────▼──────────┐
     │  Constructor   │  ← Selecciona hasta 5 activos del catálogo
     │ de Portafolio  │  → Asigna pesos con inputs numéricos
     └─────┬──────────┘    → Botón "Normalizar a 100%"
           │               → Guarda el portafolio
           │
     ┌─────▼──────────┐
     │   Simulador    │  ← Configura capital inicial, DCA, horizonte, escenarios
     │ Monte Carlo    │  → Ejecuta simulación GBM
     └─────┬──────────┘  → Muestra gráficos (fan chart, distribución, frontera)
           │             → Calcula métricas (VaR, Sharpe, CAGR, etc.)
           │
     ┌─────▼──────────┐
     │   Resultados   │  ← Historial de todas las simulaciones guardadas
     │                │  → Comparación lado a lado
     └────────────────┘  → Exportación a CSV
```

### Paso a paso:

1. **Registro/Login:** El usuario se registra con nombre de usuario, email y contraseña. La autenticación se maneja con bcrypt y sesiones de Streamlit.

2. **Perfil de Riesgo:** Un quiz de 5 preguntas clasifica al usuario en Conservador, Moderado o Agresivo. Este perfil se usa para validar que la cartera construida sea coherente con el perfil.

3. **Constructor de Portafolio:** El usuario selecciona activos del catálogo predefinido (50+ instrumentos) y asigna pesos mediante campos numéricos. Todos los campos son editables simultáneamente. Un botón "Normalizar a 100%" reescala los valores actuales para que sumen exactamente 100%. Cada portafolio se guarda con un nombre personalizado.

4. **Simulador:** Configura el capital inicial, aportación mensual DCA, ventana histórica, horizonte de proyección y número de escenarios. El motor GBM ejecuta la simulación y genera gráficos interactivos (fan chart de caminos, distribución de capital final, frontera eficiente de Markowitz).

5. **Resultados:** Todas las simulaciones guardadas se muestran en una tabla comparativa con métricas clave. Se puede eliminar simulaciones individuales o exportar todo el historial a CSV.

---

## Funcionalidades

### Perfil de Riesgo
- Quiz interactivo de 5 preguntas con ponderación por nivel de aversión
- Clasificación automática: Conservador / Moderado / Agresivo
- Los resultados se almacenan y se muestran en el Dashboard

### Constructor de Portafolio
- Catálogo de 50+ activos clasificados por tipo (stock, ETF, bond_ETF, commodity_ETF, REIT)
- Selección de hasta 5 activos con límite por `multiselect`
- Asignación de pesos mediante **inputs numéricos** (todos editables, sin sliders bloqueados)
- Botón **"Normalizar a 100%"** que reescala proporcionalmente los valores ingresados
- Visualización en barra de pesos con colores por activo
- Validación automática de suma total (debe ser 100%)
- Persistencia en archivo JSON con carga automática al Dashboard

### Simulación Monte Carlo
- **Movimiento Browniano Geométrico (GBM)** correctamente implementado
- **DCA (Dollar Cost Averaging)** corregido: las contribuciones mensuales crecen con el mercado vía `growth_factor = cum_returns[final] / cum_returns[step]`
- Capital inicial configurable (mín. $100, máx. $10M)
- Ventana histórica: 1, 3, 5, 7 o 10 años
- Horizonte de proyección: 1 a 20 años
- Escenarios: 1,000 a 15,000 simulaciones
- Parámetros de mercado: media, varianza, covarianza calculados de datos históricos reales

### Métricas de Riesgo

| Métrica | Descripción |
|---------|-------------|
| Capital Final Mediano | Tendencia central del crecimiento proyectado |
| Capital Final Esperado | Media de todos los escenarios simulados |
| VaR 95% (Valor) | Percentil 5 del capital final (valor en dólares) |
| VaR 95% (Pérdida) | Diferencia entre capital invertido y percentil 5 |
| CVaR 95% | Promedio de los escenarios peores que el VaR |
| Max Drawdown | Mayor caída desde un pico histórico proyectado |
| Sharpe Ratio | (Retorno - Tasa Libre de Riesgo) / Volatilidad |
| Sortino Ratio | Sharpe penalizando solo volatilidad negativa (downside) |
| Calmar Ratio | Retorno anualizado / Max Drawdown |
| CAGR | Tasa de Crecimiento Anual Compuesta |
| Probabilidad de Pérdida | Porcentaje de escenarios que terminan por debajo del capital inicial |

### Optimización de Markowitz
- Maximización del Ratio de Sharpe
- Minimización de la varianza (portafolio de mínima varianza)
- Frontera eficiente interactiva generada con Plotly
- Solver: `scipy.optimize.minimize` con método SLSQP
- Restricciones: pesos entre 0% y 100%, suma = 100%

### Panel de Administración
- CRUD completo de usuarios (crear, editar rol, eliminar)
- Tabla de usuarios con búsqueda y roles
- Estadísticas globales: total de usuarios, portafolios, simulaciones
- Solo accesible para usuarios con rol `admin`

### Perfil de Usuario
- Edición de nombre completo y email
- Cambio de contraseña con doble verificación
- Validación de email mediante expresión regular
- Persistencia inmediata de cambios

### Seguridad y Persistencia
- Contraseñas hasheadas con bcrypt (12 rounds)
- Sesión limpiada completamente al cerrar sesión (incluye datos de simulación y portafolio)
- Escritura atómica de archivos JSON con `os.replace()` (compatible con Windows)
- Datos almacenados en archivos JSON locales en `data/`

### Manejo de Errores
- Barrera `try/except` global en `app.py` que captura excepciones en cualquier página
- Los administradores ven el traceback completo; los usuarios ven un mensaje amigable
- Validación de entrada en todos los formularios

---

## Stack Tecnológico

| Área | Tecnología |
|------|------------|
| Lenguaje | Python 3.11+ |
| UI Framework | Streamlit 1.32+ |
| Persistencia | JSON (archivos locales) |
| Datos de Mercado | yfinance |
| Cálculo Numérico | NumPy |
| Optimización | SciPy (SLSQP) |
| DataFrames | Pandas |
| Visualizaciones | Plotly |
| Seguridad | bcrypt |
| Testing | pytest |

---

## Tests

```bash
pytest tests/ -v
```

Los tests cubren:
- **`test_monte_carlo.py`** — 15+ casos: GBM genera valores esperados, métricas dentro de rangos, DCA crece correctamente, consistencia de Sharpe y CAGR
- **`test_markowitz.py`** — 12+ casos: pesos suman 1, Sharpe máximo supera al de mínima varianza, frontera eficiente es convexa
- **`test_metrics.py`** — 18+ casos: VaR/CVaR dentro de rangos, Sharpe y Sortino consistentes, Max Drawdown no positivo

---

## Mejoras Futuras

### Navegación y UX
- **Sidebar responsiva:** Versión colapsable en dispositivos móviles o ventanas estrechas
- **Breadcrumbs:** Indicación jerárquica de la ubicación actual dentro del flujo
- **Estado activo más visible:** Resaltar la página actual en la navegación con indicador visual
- **Transiciones suaves:** Efectos de carga entre páginas para mejorar la percepción de fluidez

### Manejo de Gráficos
- **Zoom sincronizado:** Al hacer zoom en un gráfico, los demás gráficos de la misma página se actualizan en同步
- **Exportar gráficos como PNG:** Botón de descarga directa en cada gráfico Plotly
- **Tooltips mejorados:** Información adicional al pasar el mouse sobre puntos específicos (fecha exacta, valor percentil, etc.)
- **Modo comparación:** Superposición de dos simulaciones en un mismo gráfico

### Optimizaciones de Rendimiento
- **Lazy loading de datos de mercado:** Descargar datos solo cuando se accede al Simulador, no al cargar el Dashboard
- **Caché inteligente:** Precargar activos frecuentes en segundo plano
- **Simulaciones paralelas:** Distribuir escenarios Monte Carlo en múltiples hilos para reducir el tiempo de espera

### Funcionalidades Adicionales
- **Modo oscuro:** Tema alternativo para sesiones nocturnas
- **Auto-guardado:** Draft automático del portafolio mientras se edita
- **Exportación a PDF:** Reporte resumido con gráficos y métricas en un solo documento
- **Alertas personalizadas:** Notificaciones cuando una simulación supera umbrales de riesgo definidos por el usuario

---

## Errores Conocidos

- **`var_95_value` en Resultados:** La métrica `var_95_value` muestra el percentil 5 del capital final (valor en dólares, ej. $8,500), no la pérdida directa. La pérdida real está disponible como `var_95_loss` (diferencia entre capital invertido y percentil 5). Ambos valores se muestran en el Simulador, pero en Resultados solo aparece `var_95_value`. Para interpretación: si invertiste $10,000 y `var_95_value = $8,500`, la pérdida potencial es de $1,500.

---

## Deploy

### Streamlit Cloud
1. Subir el repositorio a GitHub
2. Ir a [share.streamlit.io](https://share.streamlit.io)
3. Conectar el repositorio y apuntar a `app.py`

### Render
1. Crear un nuevo Web Service
2. Build command: `pip install -r requirements.txt`
3. Start command: `streamlit run app.py --server.port \$PORT --server.headless true`
