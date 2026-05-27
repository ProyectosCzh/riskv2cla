# SmartRisk — Robo-Advisor Académico

**SmartRisk** es una plataforma de simulación estocástica y asesoramiento financiero construida con Streamlit. Permite construir portafolios de inversión a partir de un catálogo de 50+ activos reales (acciones, ETFs, bonos, REITs, commodities), simular su evolución mediante el Movimiento Browniano Geométrico (GBM) con DCA, y evaluar métricas de riesgo como VaR, CVaR, Sharpe Ratio, Sortino Ratio y Max Drawdown. Incluye optimización de Markowitz (máximo Sharpe y mínima varianza) con restricción de mínimo 5% por activo.

> **Nota:** Todas las simulaciones son proyecciones estadísticas con fines académicos. No constituyen asesoría financiera ni garantizan rendimientos futuros.

---

## Stack Tecnológico

| Área | Tecnología | Versión |
|---|---|---|
| Lenguaje | Python | ≥ 3.11 |
| UI Framework | Streamlit | ≥ 1.32.0 |
| Datos de mercado | yfinance | ≥ 0.2.36 |
| Cálculo numérico | NumPy | ≥ 1.26.0 |
| Optimización | SciPy (SLSQP) | ≥ 1.12.0 |
| Manipulación de datos | Pandas | ≥ 2.2.0 |
| Visualizaciones | Plotly | ≥ 5.19.0 |
| Autenticación | bcrypt | ≥ 4.1.2 |
| Testing | pytest | ≥ 8.0.0 |
| Persistencia | JSON (4 archivos) | — |
| Cache de mercado | JSON (archivos por ticker/años) | — |

---

## Instalación y Ejecución

```bash
# 1. Clonar el repositorio
git clone <repo-url> smartrisk
cd smartrisk

# 2. Crear entorno virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
streamlit run app.py
```

La aplicación abrirá automáticamente en `http://localhost:8501`.

> **Windows:** Todos los archivos JSON se leen con `encoding="utf-8"` de forma predeterminada. No requiere configuración adicional.

---

## Credenciales por Defecto

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador | `admin` | `Admin1234!` |

El usuario administrador se crea automáticamente en el primer inicio. Desde el panel de administración puedes crear, editar y asignar roles a otros usuarios.

---

## Estructura del Proyecto

```
smartrisk/
├── app.py                              # Punto de entrada
├── requirements.txt                    # Dependencias (8 paquetes)
├── README.md
│
├── .streamlit/
│   └── config.toml                     # Tema visual + servidor
│
├── config/
│   ├── settings.py                     # Constantes globales (paths, defaults, tasas)
│   ├── assets.json                     # Catálogo de 50 activos (7 categorías)
│   └── risk_profiles.json             # 3 perfiles de riesgo con asignación sugerida
│
├── auth/
│   ├── auth_service.py                 # Validación de registro y autenticación
│   ├── login.py                        # UI de login y registro
│   ├── password_utils.py              # Hashing bcrypt (hash + verify)
│   └── session_manager.py             # Gestión de sesión en Streamlit
│
├── database/
│   └── repositories.py                # CRUD sobre JSON (usuarios, portafolios, simulaciones, riesgo)
│
├── core/
│   ├── finance/
│   │   ├── metrics.py                  # Sharpe, Sortino, VaR, CVaR, Max Drawdown, Calmar
│   │   ├── markowitz.py               # Optimización Markowitz (SLSQP) + frontera eficiente
│   │   └── monte_carlo.py             # Motor GBM con DCA, percentiles y métricas
│   ├── market/
│   │   └── downloader.py              # Descarga yfinance + caché JSON con TTL
│   └── utils/
│       └── __init__.py                 # (vacío — validadores eliminados por no usarse)
│
├── services/
│   ├── portfolio_service.py           # Orquestación: descarga → PortfolioData → optimización
│   ├── simulation_service.py          # Orquestación: Monte Carlo → persistencia
│   ├── market_service.py              # Catálogo de activos, estadísticas, perfiles de riesgo
│   └── user_service.py               # CRUD de usuarios para administración
│
├── ui/
│   ├── components/
│   │   ├── sidebar.py                 # Navegación lateral con contexto de usuario
│   │   ├── charts.py                  # 6 funciones de gráficos Plotly
│   │   └── metrics_cards.py           # Cards, alertas, tooltips, badges
│   ├── pages/
│   │   ├── dashboard.py               # Panel principal con métricas y onboarding
│   │   ├── risk_quiz.py              # Quiz de 5 preguntas → perfil de riesgo
│   │   ├── portfolio_builder.py      # Constructor con inputs numéricos y optimización
│   │   ├── simulator.py              # Simulador Monte Carlo con 5 pestañas de gráficos
│   │   ├── results.py                # Historial de simulaciones + exportación CSV
│   │   ├── admin_panel.py            # CRUD de usuarios y estadísticas globales
│   │   └── profile.py                # Edición de perfil y cambio de contraseña
│   └── styles/
│       └── custom_css.py             # 257 líneas de CSS personalizado
│
├── tests/
│   ├── test_monte_carlo.py           # 17 tests: GBM, DCA, métricas, Sharpe/Sortino
│   ├── test_markowitz.py             # 14 tests: optimización, frontera, restricciones
│   └── test_metrics.py               # 22 tests: todas las métricas financieras
│
└── data/                              # Directorios creados automáticamente
    ├── users.json                     # Usuarios registrados
    ├── portfolios.json                # Portafolios guardados
    ├── simulations.json               # Resultados de simulaciones
    ├── risk_results.json             # Resultados del quiz de riesgo
    ├── cache/                         # Precios históricos cacheados (JSON)
    └── exports/                       # CSVs descargados por el usuario
```

---

## Arquitectura y Flujo de Datos

```
yfinance API
    │
    ▼
core/market/downloader.py
    ├── download_prices() → data/cache/TICKER_Ny.json (TTL 6h)
    ├── compute_stats()   → {mu, sigma, max_drawdown} por activo
    └── build_correlation_matrix() → returns_df + corr_matrix
    │
    ▼
services/portfolio_service.py
    └── PortfolioData (tickers, weights, prices, stats, returns_df, corr_matrix)
        ├── portfolio_mu      = weights @ mu_vec
        ├── portfolio_sigma   = sqrt(weights @ outer(sigma,sigma)*corr @ weights)
        ├── portfolio_sharpe  = (mu - rf) / sigma
        ├── portfolio_returns → weighted daily returns
        ├── historical_metrics → Sharpe, Sortino, VaR, CVaR, Drawdown, Calmar
        └── risk_profile_check → compara volatilidad con perfil de usuario
            │
            ├──► core/finance/markowitz.py
            │     ├── optimize_max_sharpe()  → OptimizationResult
            │     ├── optimize_min_variance() → OptimizationResult
            │     └── generate_efficient_frontier() → DataFrame
            │
            └──► core/finance/monte_carlo.py
                  ├── run_monte_carlo() → SimulationResult
                  │     └── GBM: S(t+dt) = S(t)*exp((μ-σ²/2)dt + σ√dt·Z)
                  └── _compute_metrics() → median, VaR, CVaR, drawdown, CAGR
                        │
                        ▼
                  database/repositories.py
                  └── save_simulation() → data/simulations.json
                        │
                        ▼
                  ui/pages/
                  ├── dashboard.py → cards + checklist
                  ├── simulator.py → 5 charts (fan, histogram, frontier, historical, correlation)
                  └── results.py   → tabla + comparación + CSV
```

### Patrones Clave

- **Cache-first download**: `downloader.py` verifica TTL de 6h antes de consultar yfinance.
- **Atomic JSON writes**: `repositories.py:_write()` usa `os.replace()` (compatible con Windows).
- **Session state como transient store**: `simulation_result` y `sim_portfolio_data` viven en `st.session_state` para persistir entre interacciones.
- **Pre-processing trigger pattern**: Botones de optimización/normalización en `portfolio_builder.py` establecen flags en session_state que se procesan ANTES de crear widgets en el siguiente render.
- **Service layer**: `portfolio_service.py` y `simulation_service.py` median entre UI y core, coordinando descargas, cálculos y persistencia.

---

## Módulos Explicados

### 5.1 Config (`config/`)

- **`settings.py`**: Única fuente de verdad para constantes: `RISK_FREE_RATE = 0.035`, `MAX_ASSETS = 5`, `MIN_WEIGHT = 0.05`, `DEFAULT_SIMULATIONS = 5000`, rutas de archivos, etc.
- **`assets.json`**: 50 activos clasificados en 7 categorías (Acciones Tecnología, Finanzas, Salud, Energía, ETFs Renta Variable, ETFs Renta Fija, Commodities y Alternativos, Tecnología e Innovación).
- **`risk_profiles.json`**: 3 perfiles (Conservador/Moderado/Agresivo) con `max_volatility`, `recommended_allocation` y `suggested_tickers`.

### 5.2 Autenticación (`auth/`)

- **`password_utils.py`**: `hash_password()` con bcrypt (12 rounds), `verify_password()`.
- **`auth_service.py`**: `register_user()` valida email con regex, username único, password ≥ 8 chars. `authenticate_user()` busca por email o username.
- **`session_manager.py`**: `init_session()`, `login_session()`, `logout_session()`, `is_authenticated()`, `is_admin()`. Maneja `st.session_state` para auth y datos de sesión.

### 5.3 Base de Datos (`database/`)

- **`repositories.py`**: CRUD completo sobre 4 archivos JSON usando `_read()`/`_write()` atómicos. UUIDs como claves. Funciones: `create_user`, `get_user_by_email`, `save_portfolio`, `get_portfolios_for_user`, `save_simulation`, `save_risk_profile`, etc.

### 5.4 Core Financiero (`core/finance/`)

#### `metrics.py` — Métricas de Riesgo-Retorno

| Función | Fórmula | Descripción |
|---|---|---|
| `annualized_return(returns)` | `(∏(1+r))^(252/n) - 1` | Retorno geométrico anualizado |
| `annualized_volatility(returns)` | `σ(r) · √252` | Volatilidad anualizada |
| `sharpe_ratio(returns, rf=0.035)` | `(μ - rf) / σ` | Exceso de retorno por unidad de riesgo total |
| `sortino_ratio(returns, rf=0.035)` | `(μ - rf) / σ_downside` | Exceso de retorno por unidad de riesgo downside |
| `max_drawdown(prices)` | `min((P - peak) / peak)` | Máxima caída desde pico a valle |
| `value_at_risk(returns, 0.95)` | `-P5(returns)` | Pérdida mínima esperada en el peor 5% |
| `conditional_var(returns, 0.95)` | `E[returns \| returns ≤ -VaR]` | Pérdida promedio más allá del VaR |
| `calmar_ratio(returns, prices)` | `μ / \|MDD\|` | Retorno por unidad de máximo drawdown |
| `compute_all_metrics(returns, prices, rf)` | Agrega todas las anteriores | Diccionario completo |

#### `markowitz.py` — Optimización de Portafolio

- **`_portfolio_stats(weights, mu, cov, rf)`**: Calcula retorno, volatilidad y Sharpe para un vector de pesos.
- **`optimize_max_sharpe(mu, cov, rf, tickers)`**: Maximiza Sharpe vía SLSQP. Bounds `[MIN_WEIGHT, 1.0]` (= `[0.05, 1.0]`), constraint `sum(weights)=1`.
- **`optimize_min_variance(mu, cov, rf, tickers)`**: Minimiza varianza. Mismas constraints.
- **`generate_efficient_frontier(mu, cov, rf, n_points=60)`**: Barre retornos objetivo y minimiza varianza para cada uno. Retorna DataFrame con `volatility`, `return`, `sharpe`.

#### `monte_carlo.py` — Simulación GBM

- **`SimulationConfig`**: Dataclass con tickers, weights, mu_vec, sigma_vec, corr_matrix, capital, DCA, años, simulaciones, seed.
- **`run_monte_carlo(cfg)`**: Simula portafolio como proceso GBM escalar:
  1. `port_mu = weights @ mu_vec`
  2. `port_var = weights @ (outer(sigma,sigma) * corr) @ weights`
  3. Genera `Z ~ N(0,1)` de forma `(n_sims, n_steps)`
  4. `log_returns = (port_mu - 0.5 * port_sigma²) · dt + port_sigma · √dt · Z`
  5. `paths = initial_capital · exp(cumsum(log_returns))`
  6. **DCA**: Aportaciones mensuales crecen con `growth_factor = cum_returns[:, -1] / cum_returns[:, step]`
- **`_compute_metrics(result)`**: expected_capital, median_capital, var_95, cvar_95, max_drawdown, prob_loss, cagr_median, total_invested.
- **`compute_sharpe(mu, sigma, risk_free_rate)`**: Sharpe desde parámetros del modelo (no desde returns).
- **`compute_sortino(returns, risk_free_rate)`**: Sortino desde returns (downside < 0).

### 5.5 Core de Mercado (`core/market/`)

- **`downloader.py`**: `download_prices(ticker, years)` → descarga vía `yfinance.download()` y cachea como JSON. `download_multiple(tickers, years)` con `time.sleep(0.05)` entre requests. `compute_returns()` → log returns. `compute_stats()` → mu, sigma, max_drawdown. `build_correlation_matrix()` → Pearson sobre returns alineados.

### 5.6 Servicios (`services/`)

- **`portfolio_service.py`**: `PortfolioData` (clase contenedora), `build_portfolio_data()` (descarga + computa stats), `run_markowitz_optimization()` (envuelve optimizadores con `RISK_FREE_RATE`), `compute_efficient_frontier()`. La clase tiene propiedades calculadas (`portfolio_mu`, `portfolio_sigma`, `portfolio_sharpe`), `portfolio_returns()`, `historical_metrics()`, `risk_profile_check()`.
- **`simulation_service.py`**: `build_simulation_config()` + `run_simulation()` + `persist_simulation()`.
- **`market_service.py`**: `get_asset_catalog()`, `get_asset_info()`, `fetch_asset_stats()`, `get_quick_stats_table()`, `get_risk_profiles()`.
- **`user_service.py`**: `list_users()`, `get_user()`, `deactivate_user()`, `activate_user()`, `promote_to_admin()`, `remove_user()`.

### 5.7 UI (`ui/`)

#### Páginas (7 pantallas):

1. **Dashboard** (`dashboard.py`): 4 metric cards, checklist de 4 pasos, resumen de perfil de riesgo, últimas 3 simulaciones.
2. **Perfil de Riesgo** (`risk_quiz.py`): 5 preguntas con radio buttons, clasifica en Conservador/Moderado/Agresivo, muestra perfil con icono y tickers sugeridos.
3. **Constructor de Portafolio** (`portfolio_builder.py`): Multiselect de hasta 5 activos, inputs numéricos por activo, botones Normalizar/Max Sharpe/Min Riesgo, barra visual de pesos, guardar/recuperar.
4. **Simulador Monte Carlo** (`simulator.py`): Selector de portafolio, parámetros (capital, DCA, ventana histórica, proyección, simulaciones), 8 metric cards, 5 tabs (Proyección/Distribución/Frontera Eficiente/Histórico/Correlaciones), exportación CSV.
5. **Resultados** (`results.py`): Tabla de simulaciones guardadas, comparación lado a lado, eliminar, exportar CSV.
6. **Admin Panel** (`admin_panel.py`): 3 tabs (lista/crear/editar usuarios), 4 métricas globales.
7. **Perfil de Usuario** (`profile.py`): 3 tabs (información/seguridad/estadísticas).

#### Componentes:

- **`sidebar.py`**: Logo, info de usuario, 6 botones de navegación + admin + logout.
- **`charts.py`**: `plot_monte_carlo_paths()` (fan chart con bandas percentiles), `plot_final_value_histogram()` (histograma + VaR/líneas), `plot_efficient_frontier()` (scatter coloreado por Sharpe), `plot_portfolio_weights()` (donut), `plot_historical_performance()` (series normalizadas), `plot_correlation_heatmap()` (heatmap RdBu).
- **`metrics_cards.py`**: `metric_card()`, `alert_box()`, `tooltip_box()`, `section_header()`, `page_header()`, `risk_badge()`, `spacer()`.

### 5.8 Tests (`tests/`)

```bash
pytest tests/ -v    # 54 tests, ~11s
```

- **`test_metrics.py`** (22 tests): annualized_return (4), annualized_volatility (3), sharpe_ratio (4), sortino_ratio (2), max_drawdown (4), VaR/CVaR (3), compute_all_metrics (2).
- **`test_markowitz.py`** (14 tests): max_sharpe (7), min_variance (4), efficient_frontier (3).
- **`test_monte_carlo.py`** (17 tests): GBM basics (7), metrics (6), DCA (1), Sharpe/Sortino (4).

---

## Guía de Usuario

### Flujo de Trabajo Recomendado

```
Registro / Login
       │
       ▼
   Dashboard          ← Resumen de portafolios, simulaciones y perfil
       │
       ▼
   Perfil de Riesgo   ← Quiz de 5 preguntas → Conservador / Moderado / Agresivo
       │
       ▼
   Constructor de     ← Selecciona hasta 5 activos del catálogo
   Portafolio         → Asigna pesos con inputs numéricos
                      → Normaliza a 100% u optimiza con Markowitz
                      → Guarda el portafolio
       │
       ▼
   Simulador Monte    ← Configura capital, DCA, horizonte, escenarios
   Carlo              → Ejecuta simulación GBM
                      → Muestra 5 gráficos + 8 métricas
       │
       ▼
   Resultados         ← Historial de simulaciones guardadas
                      → Comparación lado a lado + exportación CSV
```

### Pantalla por Pantalla

#### 1. Login / Register
- Dos tabs: Iniciar Sesión y Crear Cuenta.
- Registro: nombre completo, username, email (validado con regex), contraseña (mín. 8 caracteres).
- Demo account: `admin` / `Admin1234!`.

#### 2. Dashboard
- Bienvenida personalizada con nombre de usuario.
- 4 tarjetas: portafolios guardados, simulaciones ejecutadas, perfil de riesgo, última simulación.
- Checklist de 4 pasos (Perfil → Portafolio → Simular → Resultados).
- Resumen del perfil de riesgo con icono, puntaje y descripción.

#### 3. Perfil de Riesgo
- 5 preguntas con 3 opciones cada una (puntaje 1-3 → total 5-15).
- Clasificación: Conservador (5-8), Moderado (9-11), Agresivo (12-15).
- Muestra el perfil asignado con max_volatility, asignación recomendada y tickers sugeridos.

#### 4. Constructor de Portafolio
- Catálogo plano de 50 activos con búsqueda en multiselect (máx. 5).
- Inputs numéricos por activo (0-100%, step 0.1).
- Botón **"Normalizar a 100%"**: reescala proporcionalmente los valores actuales.
- Botón **"Maximizar Sharpe"**: descarga datos históricos, ejecuta optimización Markowitz, asigna pesos óptimos.
- Botón **"Minimizar Riesgo"**:同上, minimiza varianza.
- Barra visual de pesos con colores por activo + leyenda.
- Validación de suma (debe ser 100% ± 0.5%).
- Guardar con nombre personalizado + auto-carga al Simulador.

#### 5. Simulador Monte Carlo
- Selecciona portafolio (borrador o guardado).
- Parámetros: capital inicial ($100-$10M), DCA mensual ($0-$100K), ventana histórica (1/3/5/7/10 años), horizonte (1-20 años), simulaciones (1K-15K).
- Alerta de perfil de riesgo si la volatilidad excede el límite del perfil.
- **8 tarjetas de métricas**: Capital Mediano, VaR 95%, Max Drawdown, Prob. Pérdida, Sharpe, Volatilidad, Retorno Esperado, CVaR 95%.
- **5 pestañas de gráficos Plotly**:
  1. **Proyección**: Fan chart con bandas 5-95% y 25-75%, líneas P5/P50/P95.
  2. **Distribución**: Histograma de capital final + donut de pesos.
  3. **Frontera Eficiente**: Scatter coloreado por Sharpe, marcadores para portafolio actual y óptimo.
  4. **Histórico**: Rendimiento normalizado (base 100) + tabla de stats por activo.
  5. **Correlaciones**: Heatmap de correlación entre activos.
- Exportación CSV con todas las métricas.

#### 6. Resultados
- Tabla de todas las simulaciones guardadas (portafolio, capital, VaR, drawdown, CAGR, fecha).
- Comparación lado a lado: selecciona 2 simulaciones y compara métricas.
- Eliminar simulaciones individuales.
- Exportar historial completo a CSV.

#### 7. Perfil de Usuario
- Tab Información: avatar con iniciales, nombre, email, username (solo lectura).
- Tab Seguridad: cambio de contraseña con verificación de actual + confirmación.
- Tab Estadísticas: portafolios guardados, simulaciones ejecutadas, perfil de riesgo, mejor simulación.

#### 8. Admin Panel
- Solo accesible con rol `admin`.
- 4 métricas globales: usuarios totales, admins, simulaciones totales, portafolios totales.
- Lista de usuarios en DataFrame, crear usuario, editar/eliminar usuario.

---

## Seguridad

- **Contraseñas**: hasheadas con bcrypt (12 rounds). Nunca almacenadas en texto plano.
- **Sesiones**: `st.session_state` con limpieza completa al cerrar sesión (incluye datos de simulación y portafolio).
- **Escritura atómica**: `os.replace()` para evitar corrupción de archivos JSON en Windows.
- **Encoding**: `utf-8` en toda lectura/escritura de archivos para evitar UnicodeDecodeError.
- **Validación de email**: expresión regular en `auth_service.py`.
- **Error handling**: Barrera `try/except` global en `app.py`. Admins ven traceback completo; usuarios ven mensaje amigable.

---

## Configuración

### `config/settings.py`
Constantes principales editables:
- `RISK_FREE_RATE = 0.035` — Tasa libre de riesgo (proxy T-Bill)
- `MAX_ASSETS = 5` — Máximo de activos por portafolio
- `MIN_WEIGHT = 0.05` — Peso mínimo por activo (5%)
- `DEFAULT_SIMULATIONS = 5000` — Escenarios por defecto
- `MAX_SIMULATIONS = 15000` — Escenarios máximos
- `DEFAULT_INITIAL_CAPITAL = 10000`
- `CACHE_EXPIRY_HOURS = 6` — TTL del caché de precios

### `config/assets.json`
Agrega o modifica activos en las 7 categorías. Cada activo requiere: `ticker`, `name`, `type` (stock|etf|bond_etf|commodity_etf|reit).

### `config/risk_profiles.json`
Define perfiles con: `label`, `color`, `icon`, `description`, `max_volatility`, `recommended_allocation`, `suggested_tickers`.

### `.streamlit/config.toml`
Tema visual (colores institucionales #1B3A6B), server headless, CORS deshabilitado.

---

## Tests

```bash
pytest tests/ -v
```

**54 tests** distribuidos:

| Archivo | Tests | Cobertura |
|---|---|---|
| `test_metrics.py` | 22 | Sharpe, Sortino, VaR, CVaR, Drawdown, Calmar, Return, Volatility |
| `test_markowitz.py` | 14 | Max Sharpe, Min Variance, Efficient Frontier, constraints |
| `test_monte_carlo.py` | 17 | GBM paths, percentiles, DCA, Sharpe/Sortino, metrics |

---

## Mejoras Futuras

- **Base de datos real**: Migrar de JSON a SQLite/PostgreSQL para concurrencia multi-usuario.
- **Logging estructurado**: Reemplazar prints por `logging` con niveles.
- **Simulaciones paralelas**: Distribuir escenarios Monte Carlo en múltiples hilos.
- **Exportación a PDF**: Reporte resumido con gráficos y métricas.
- **Modo oscuro**: Tema alternativo para sesiones nocturnas.
- **Alertas personalizadas**: Notificaciones cuando una simulación supera umbrales de riesgo.
- **Zoom sincronizado entre gráficos**: Al hacer zoom en un gráfico, actualizar los demás.
- **Breadcrumbs**: Indicación jerárquica de ubicación en el flujo.
- **Lazy loading**: Descargar datos de mercado solo al acceder al Simulador.

---

## Deploy

### Streamlit Cloud
1. Subir el repositorio a GitHub.
2. Ir a [share.streamlit.io](https://share.streamlit.io).
3. Conectar el repositorio y apuntar a `app.py`.

### Render
1. Crear un nuevo Web Service.
2. Build command: `pip install -r requirements.txt`.
3. Start command: `streamlit run app.py --server.port $PORT --server.headless true`.
