# SmartRisk — Robo-Advisor Académico

**SmartRisk** es una plataforma web de simulación financiera y asesoramiento automatizado de portafolios, desarrollada como proyecto final de la materia **SI210M1 — Estructura de Datos**. Aplica los conceptos fundamentales de la materia (pilas, colas, árboles, ordenamiento, hashing, TADs, matrices, manejo de cadenas, persistencia) a un problema real: la construcción, optimización y simulación de portafolios de inversión mediante métodos de Financial Engineering.

> **Nota:** Todas las simulaciones son proyecciones estadísticas con fines académicos. No constituyen asesoría financiera ni garantizan rendimientos futuros.

---

## Stack Tecnológico

| Área | Tecnología | Versión Mínima | Propósito |
|---|---|---|---|
| Lenguaje | Python | ≥ 3.11 | Tipado moderno, ecosistema científico |
| UI Framework | Streamlit | ≥ 1.32.0 | Prototipado rápido de dashboards |
| Datos de Mercado | yfinance | ≥ 0.2.36 | Descarga gratuita de precios históricos |
| Cálculo Numérico | NumPy | ≥ 1.26.0 | Álgebra lineal, GBM, estadísticas |
| Optimización | SciPy | ≥ 1.12.0 | SLSQP para frontera eficiente |
| Manipulación de Datos | Pandas | ≥ 2.2.0 | Series temporales, correlaciones |
| Visualizaciones | Plotly | ≥ 5.19.0 | Gráficos interactivos (Heatmap, Histograma, Líneas) |
| Autenticación | bcrypt | ≥ 4.1.2 | Hashing de contraseñas (12 rounds) |
| Persistencia | JSON (archivos planos) | — | Sharding por usuario con escritura atómica |

---

## Estructura del Proyecto

```
smartrisk/
├── app.py                              # Punto de entrada Streamlit
├── requirements.txt                    # Dependencias pip
├── README.md                           # Este documento
│
├── .streamlit/
│   └── config.toml                     # Tema visual (navy/light) + servidor headless :8501
│
├── config/                             # 📁 Configuración estática
│   ├── settings.py                     # Constantes globales (rutas, límites, defaults)
│   ├── assets.json                     # Catálogo de 50 activos en 7 categorías
│   ├── risk_profiles.json              # 3 perfiles de riesgo (conservador/moderado/agresivo)
│   └── risk_quiz.py                    # 5 preguntas del quiz + función classify_profile()
│
├── auth/                               # 📁 Autenticación y sesión
│   ├── auth_service.py                 # register_user() y authenticate_user() — orquesta validación + persistencia
│   ├── password_utils.py               # hash_password() y verify_password() con bcrypt
│   └── session_manager.py              # init_session(), login_session(), logout_session(), is_admin()
│
├── core/                               # 📁 Núcleo financiero y estructuras de datos
│   ├── exceptions.py                   # Jerarquía SmartRiskError (4 subclases)
│   ├── ds/                             # 📌 Estructuras de Datos (SI210)
│   │   ├── queue.py                    # DownloadQueue — FIFO con lista enlazada simple
│   │   ├── stack.py                    # SimulationStack — LIFO con lista doblemente enlazada
│   │   ├── sorting.py                  # SimulationSorter — QuickSort / MergeSort
│   │   └── tree_traversal.py          # AssetCategoryTree — árbol N-ario con recorrido recursivo
│   ├── finance/
│   │   ├── markowitz.py                # Optimización SLSQP: max_sharpe, min_variance, frontera eficiente
│   │   └── monte_carlo.py              # Motor GBM con Cholesky, DCA, 8 métricas de riesgo
│   ├── market/
│   │   └── downloader.py               # Descarga yfinance + caché JSON (TTL 6h) + DownloadQueue
│   └── utils/
│       └── string_validator.py         # Validación regex de email, password, username, ticker
│
├── database/                           # 📁 Capa de persistencia
│   └── repositories.py                 # CRUD usuarios, portafolios, simulaciones, riesgo sobre JSON
│
├── services/                           # 📁 Orquestación de lógica de negocio
│   ├── portfolio_service.py            # PortfolioData (TAD) + build_portfolio_data() + optimización
│   ├── simulation_service.py           # run_simulation() + persist_simulation()
│   └── market_service.py               # get_asset_catalog(), get_risk_profiles(), flat_asset_list()
│
├── ui/                                 # 📁 Interfaz de usuario
│   ├── assets/
│   │   ├── logorisk.jpg                # Logo de la aplicación
│   │   └── __init__.py                 # get_logo_img_tag() — carga y cachea logo en base64
│   ├── components/
│   │   ├── sidebar.py                  # Navegación lateral con botones de página
│   │   ├── charts.py                   # 4 gráficos Plotly (Monte Carlo, histograma, dona, histórico)
│   │   └── metrics_cards.py            # Componentes HTML reutilizables (metric_card, alert_box, tooltip_box, etc.)
│   ├── pages/
│   │   ├── login.py                    # Login + Registro con tabs
│   │   ├── dashboard.py                # Panel principal con checklist de 4 pasos
│   │   ├── risk_quiz.py                # Quiz de 5 preguntas → clasificación de perfil
│   │   ├── portfolio_builder.py        # Constructor con árbol recursivo + optimización Markowitz
│   │   ├── simulator.py                # Simulador Monte Carlo + SimulationStack LIFO
│   │   ├── results.py                  # Historial ordenable con SimulationSorter
│   │   ├── admin_panel.py              # CRUD de usuarios (admin only)
│   │   └── profile.py                  # Perfil, cambio de contraseña, estadísticas
│   └── styles/
│       └── custom_css.py               # 261 líneas de CSS profesional (tema navy/slate)
│
└── data/                               # 📁 Creado automáticamente al ejecutar
    ├── users/                          # {user_id}.json por usuario
    ├── portfolios/                     # {user_id}.json por usuario
    ├── simulations/                    # {user_id}.json por usuario
    ├── risk_results/                   # {user_id}.json por usuario
    └── cache/                          # {ticker}_{years}y.json — TTL 6 horas
```

---

## Mapa de Archivos (Dependencias y Propósito)

### Archivos Raíz

| Archivo | Propósito | Importa de | Exporta |
|---|---|---|---|
| `app.py` | Bootstrap Streamlit: config de página, CSS, sesión, admin, directorios, ruteo a páginas | `auth/`, `ui/pages/*`, `ui/components/sidebar`, `ui/styles/custom_css`, `database/repositories` | `main()`, `PAGE_MAP` |
| `requirements.txt` | Dependencias pip congeladas | — | — |

### Config (`config/`)

| Archivo | Propósito | Exporta |
|---|---|---|
| `settings.py` | 25 constantes: rutas de directorios, límites de simulación, restricciones de portafolio | `BASE_DIR`, `DATA_DIR`, `USERS_DIR`, `PORTFOLIOS_DIR`, `SIMULATIONS_DIR`, `RISK_RESULTS_DIR`, `CACHE_DIR`, `DEFAULT_SIMULATIONS=5000`, `MAX_SIMULATIONS=15000`, `MAX_ASSETS=5`, `MIN_WEIGHT=0.05`, `MAX_WEIGHT=1.0`, `CACHE_EXPIRY_HOURS=6`, `RISK_FREE_RATE=0.035`, `ROLE_ADMIN="admin"` |
| `assets.json` | 50 tickers en 7 categorías (Tecnología, Finanzas, Salud, Energía, ETFs RV, ETFs RF, Commodities, Innovación) | `categories` → dict con nombre de categoría → lista de `{ticker, name, type}` |
| `risk_profiles.json` | 3 perfiles: conservador (vol ≤ 12%), moderado (vol ≤ 20%), agresivo (vol ≤ 100%) | `label`, `color`, `icon`, `description`, `max_volatility`, `recommended_allocation`, `suggested_tickers` |
| `risk_quiz.py` | 5 preguntas con 3 opciones (score 1-3 c/u) + clasificador | `QUESTIONS` (list), `classify_profile(score) → str` |

### Auth (`auth/`)

| Archivo | Propósito | Importa de | Exporta |
|---|---|---|---|
| `auth_service.py` | Orquesta registro y autenticación: valida con `StringValidator`, hashea con bcrypt, persiste con repositorios | `password_utils`, `core/exceptions`, `core/utils/string_validator`, `database/repositories` | `register_user(username, email, password, full_name) → dict`, `authenticate_user(username_or_email, password) → dict\|None` |
| `password_utils.py` | Hashing y verificación bcrypt (12 rounds) | `bcrypt` | `hash_password(plain) → str`, `verify_password(plain, hashed) → bool` |
| `session_manager.py` | Manejo de sesión via `st.session_state` | `streamlit`, `config/settings` | `init_session()`, `login_session(user)`, `logout_session()`, `get_current_user()`, `is_authenticated()`, `is_admin()` |

### Core — Excepciones (`core/`)

| Archivo | Propósito | Exporta |
|---|---|---|
| `exceptions.py` | Jerarquía de 5 clases: `SmartRiskError(Exception)` → `AuthError`, `ValidationError`, `DataError`, `SimulationError` | Cada clase con `__init__(message, code)` y `__str__` formateado |

### Core — Estructuras de Datos (`core/ds/`)

| Archivo | Estructura | Unidad Sílabo | Exporta |
|---|---|---|---|
| `queue.py` | `_Node` (data, next) + `DownloadQueue` — FIFO con **lista enlazada simple** | VII — Colas | `enqueue(item)`, `dequeue() → item`, `peek()`, `is_empty()`, `clear()`, `size` (property), `__iter__`, `__repr__` |
| `stack.py` | `_Node` (data, prev, next) + `SimulationStack` — LIFO con **lista doblemente enlazada** | VI — Pilas | `push(item)`, `pop() → item`, `peek()`, `is_empty()`, `clear()`, `size` (property), `items() → list` |
| `sorting.py` | `SimulationSorter` — **QuickSort** (n > 10) y **MergeSort** (n ≤ 10) estables | VIII — Ordenamiento | `sort(items, key, reverse) → list`, `merge_sort(items, key, reverse)`, `quick_sort(items, key, reverse)`, `ALGORITHM` (class attr) |
| `tree_traversal.py` | `AssetTreeNode` (name, children, data) + `AssetCategoryTree` — árbol N-ario con **recorrido recursivo pre-order y post-order** | II — Recursividad | `traverse_preorder() → list[dict]`, `traverse_postorder() → list[str]`, `find_by_ticker(ticker) → AssetTreeNode\|None` |

### Core — Finanzas (`core/finance/`)

| Archivo | Propósito | Exporta |
|---|---|---|
| `markowitz.py` | Optimización de portafolios via SLSQP. Dataclass `OptimizationResult`. Generación de frontera eficiente | `optimize_max_sharpe(mu, cov, rf, tickers) → OptimizationResult`, `optimize_min_variance(mu, cov, rf, tickers) → OptimizationResult`, `generate_efficient_frontier(mu, cov, rf, n_points) → DataFrame` |
| `monte_carlo.py` | Motor de simulación GBM con Cholesky. Dataclasses `SimulationConfig` y `SimulationResult`. Cálculo de 8 métricas | `run_monte_carlo(cfg) → SimulationResult` |

### Core — Mercado y Utilidades

| Archivo | Propósito | Exporta |
|---|---|---|
| `core/market/downloader.py` | Descarga de precios vía yfinance con caché JSON (TTL 6h). Cola FIFO para descarga múltiple | `_download_prices(ticker, years) → Series\|None`, `download_multiple(tickers, years, progress_callback) → dict`, `_compute_returns(prices) → Series`, `compute_stats(prices) → dict`, `build_correlation_matrix(prices_dict) → (returns_df, corr_df)` |
| `core/utils/string_validator.py` | Validación de cadenas con regex | `validate_email(email) → (bool, str)`, `validate_password(password) → (bool, str)`, `validate_username(username) → (bool, str)`, `validate_ticker(ticker) → (bool, str)`, `sanitize_ticker(ticker) → str` |

### Database

| Archivo | Propósito | Exporta |
|---|---|---|
| `repositories.py` | CRUD JSON atómico (`tmp` + `os.replace`) con sharding por usuario | Usuarios: `get_all_users()`, `get_user_by_email()`, `get_user_by_username()`, `create_user()`, `update_user()`, `delete_user()`, `ensure_admin_exists()` — Portafolios: `get_portfolios_for_user()`, `save_portfolio()`, `delete_portfolio()` — Simulaciones: `get_simulations_for_user()`, `save_simulation()`, `delete_simulation()` — Riesgo: `get_risk_profile_for_user()`, `save_risk_profile()` |

### Services

| Archivo | Propósito | Importa de | Exporta |
|---|---|---|---|
| `portfolio_service.py` | Clase `PortfolioData` (TAD con propiedades computadas) + funciones de construcción y optimización | `core/market/downloader`, `core/finance/markowitz`, `config/settings` | `PortfolioData` (clase), `build_portfolio_data(tickers, weights, history_years, progress_callback) → PortfolioData\|None`, `run_markowitz_optimization(portfolio_data, method) → OptimizationResult`, `equal_weights_dict(tickers) → dict` |
| `simulation_service.py` | Orquesta simulación + persistencia | `core/finance/monte_carlo`, `services/portfolio_service`, `database/repositories` | `run_simulation(portfolio_data, initial_capital, monthly_dca, projection_years, n_simulations, seed) → SimulationResult`, `persist_simulation(user_id, portfolio_data, result) → dict` |
| `market_service.py` | Carga datos de activos y perfiles desde JSON | `config/settings` | `get_asset_catalog() → dict`, `get_risk_profiles() → dict`, `flat_asset_list(assets_data) → list[dict]` |

### UI — Componentes

| Archivo | Propósito | Exporta |
|---|---|---|
| `sidebar.py` | Barra lateral con logo, info de usuario, navegación (6 páginas usuario + 1 admin), botón cerrar sesión | `render_sidebar()` |
| `charts.py` | 4 gráficos Plotly con paleta navy/slate | `plot_monte_carlo_paths(paths, projection_years, initial_capital) → Figure`, `plot_final_value_histogram(final_values, initial_capital) → Figure`, `plot_portfolio_weights(tickers, weights) → Figure`, `plot_historical_performance(prices_dict, weights, tickers) → Figure` |
| `metrics_cards.py` | Componentes HTML reutilizables con estilo CSS | `metric_card(label, value, delta, color)`, `alert_box(message, alert_type)`, `tooltip_box(text)`, `section_header(title, subtitle)`, `page_header(title, subtitle)`, `spacer(height)` |

### UI — Páginas

| Archivo | Ruta | Propósito |
|---|---|---|
| `login.py` | `/` (no auth) | Login con `authenticate_user()`, registro con `register_user()`. Captura `AuthError` y `ValidationError` con caption didáctico de herencia de excepciones |
| `dashboard.py` | `dashboard` | Checklist 4 pasos, perfil de riesgo, últimas 3 simulaciones, métricas rápidas |
| `risk_quiz.py` | `risk_quiz` | 5 preguntas del quiz → `classify_profile()` → `save_risk_profile()`. Muestra detalle del perfil y activos sugeridos |
| `portfolio_builder.py` | `portfolio` | Árbol recursivo de categorías, selector multiselect (max 5), inputs de pesos, normalización, optimización Markowitz (max_sharpe/min_variance), barra visual de pesos, guardado. Valida tickers con `StringValidator.validate_ticker()` |
| `simulator.py` | `simulator` | Selección de portafolio, parámetros (capital, DCA, ventana histórica, proyección, N simulaciones), descarga FIFO con barra de progreso, simulación GBM, pila LIFO (`SimulationStack`) con navegación (descartar/recuperar), 3 tabs de resultados, alerta de perfil de riesgo |
| `results.py` | `results` | Historial ordenable por Capital/VaR/CAGR via `SimulationSorter`, mejor/peor escenario destacado, eliminación de simulaciones |
| `admin_panel.py` | `admin` | CRUD completo de usuarios: listar, crear (con `StringValidator`), editar rol/activo, eliminar. Solo accesible con rol admin |
| `profile.py` | `profile` | 3 tabs: información personal, cambio de contraseña (con verificación actual + `StringValidator`), estadísticas de actividad |

### UI — Assets y Styles

| Archivo | Propósito |
|---|---|
| `ui/assets/__init__.py` | Carga `logorisk.jpg` en base64 con cacheo (`@st.cache_data`), exporta `get_logo_img_tag(height) → str` |
| `ui/assets/logorisk.jpg` | Logo de la aplicación (usado en sidebar y login) |
| `ui/styles/custom_css.py` | 261 líneas de CSS con: variables navy/slate, sidebar oscura, metric cards con sombra, alert boxes (4 tipos), badges de perfil, tooltips, scrollbar personalizada, ocultación de branding Streamlit |

## Reglas de Negocio

### Constantes Globales (`config/settings.py`)

| Constante | Valor | Límite |
|---|---|---|
| `DEFAULT_SIMULATIONS` | 5,000 | — |
| `MAX_SIMULATIONS` | 15,000 | — |
| `DEFAULT_INITIAL_CAPITAL` | $10,000 USD | Mín $100, Máx $10M |
| `DEFAULT_MONTHLY_DCA` | $0 | Máx $100,000 |
| `DEFAULT_PROJECTION_YEARS` | 5 años | 1-20 años |
| `DEFAULT_HISTORY_YEARS` | 5 años | 1-10 años |
| `MAX_ASSETS` | 5 activos | Por portafolio |
| `MIN_WEIGHT` | 0.05 (5%) | Por activo en optimización |
| `MAX_WEIGHT` | 1.0 (100%) | Por activo en optimización |
| `RISK_FREE_RATE` | 0.035 (3.5%) | Tasa libre de riesgo anual |
| `CACHE_EXPIRY_HOURS` | 6 horas | TTL de caché de precios |
| `ROLE_ADMIN` | `"admin"` | String de rol |

### Perfiles de Riesgo

| Perfil | Score Quiz | Volatilidad Máx | Asignación Recomendada | Tickers Sugeridos |
|---|---|---|---|---|
| Conservador | 5-7 pts | ≤ 12% anual | Bonos 60% / RV 30% / Cash 10% | BND, TLT, VCSH, AGG, SHY |
| Moderado | 8-12 pts | ≤ 20% anual | Bonos 35% / RV 60% / Cash 5% | SPY, QQQ, BND, VTI, SCHD |
| Agresivo | 13-15 pts | ≤ 100% anual | Bonos 5% / RV 90% / Cash 5% | QQQ, ARKK, NVDA, TSLA, META |

### Quiz de Riesgo (`config/risk_quiz.py`)

5 preguntas con 3 opciones cada una (score 1-3):
1. **Objetivo de inversión** (preservar=1, moderado=2, maximizar=3)
2. **Reacción a pérdida del 20%** (vender=1, esperar=2, comprar más=3)
3. **Horizonte temporal** (<2a=1, 3-7a=2, >10a=3)
4. **Experiencia** (principiante=1, intermedio=2, avanzado=3)
5. **Escenario atractivo** (4% seguro=1, 10% volátil=2, 25% muy volátil=3)

Total: 5-15 pts → `classify_profile(score)` → conservador (≤7), moderado (8-12), agresivo (≥13)

---

## Arquitectura y Flujo de Datos

### Diagrama de Llamadas

```
app.py:main()
│
├── inject_css()                     → custom_css.py
├── init_session()                   → session_manager.py
├── ensure_admin_exists()            → repositories.py
├── ensure_directories()             → settings.py
│
├── [no auth] render_login()
│   ├── authenticate_user()          → auth_service.py → password_utils.py + repositories.py
│   └── register_user()              → auth_service.py → StringValidator + password_utils + repositories
│
└── [auth] render_sidebar()
    └── render_<page>()
        │
        ├── render_dashboard()
        │   ├── get_portfolios_for_user()  → repositories.py
        │   ├── get_simulations_for_user() → repositories.py
        │   └── get_risk_profile_for_user()→ repositories.py
        │
        ├── render_risk_quiz()
        │   ├── get_risk_profiles()       → market_service.py → risk_profiles.json
        │   ├── classify_profile()        → risk_quiz.py
        │   └── save_risk_profile()       → repositories.py
        │
        ├── render_portfolio_builder()
        │   ├── AssetCategoryTree()       → tree_traversal.py (recorrido recursivo)
        │   ├── StringValidator           → string_validator.py
        │   ├── get_asset_catalog()       → market_service.py → assets.json
        │   ├── build_portfolio_data()    → portfolio_service.py
        │   │   └── download_multiple()   → downloader.py (DownloadQueue FIFO)
        │   ├── run_markowitz_optimization() → portfolio_service.py → markowitz.py (SLSQP)
        │   └── save_portfolio()          → repositories.py
        │
        ├── render_simulator()
        │   ├── build_portfolio_data()    → portfolio_service.py
        │   ├── run_simulation()          → simulation_service.py → monte_carlo.py (GBM)
        │   ├── persist_simulation()      → repositories.py
        │   ├── SimulationStack LIFO      → stack.py (navegación push/pop/peek)
        │   └── chart functions           → charts.py (Plotly)
        │
        ├── render_results()
        │   ├── get_simulations_for_user()→ repositories.py
        │   └── SimulationSorter.sort()   → sorting.py (QuickSort/MergeSort)
        │
        ├── render_admin_panel()
        │   ├── get_all_users()           → repositories.py
        │   ├── register_user()           → auth_service.py
        │   └── update_user/delete_user() → repositories.py
        │
        └── render_profile()
            ├── update_user()             → repositories.py
            ├── hash_password/verify      → password_utils.py
            └── StringValidator           → string_validator.py
```

### Flujo de Datos Financiero

```
Usuario selecciona tickers y pesos
        │
        ▼
build_portfolio_data()
        │
        ├── download_multiple(tickers)
        │       │
        │       ├── DownloadQueue.enqueue(cada ticker)
        │       ├── while queue: _download_prices(ticker)
        │       │       ├── ¿Cache válido? → load cache JSON
        │       │       └── No → yfinance.download() → save cache JSON
        │       └── return {ticker: pd.Series}
        │
        ├── compute_stats() → {mu (anual), sigma (anual), max_drawdown}
        ├── build_correlation_matrix() → (returns_df, corr_df)
        │
        └── PortfolioData(tickers, weights, prices, stats, returns, corr)
                │  .mu_vec        = np.array([stats[t]["mu"] for t in tickers])
                │  .sigma_vec     = np.array([stats[t]["sigma"] for t in tickers])
                │  .corr_array    = corr_matrix.values
                │  .portfolio_mu  = w @ mu_vec
                │  .portfolio_sigma = sqrt(w @ (outer(sigma,sigma)*corr) @ w)
                │  .portfolio_sharpe = (portfolio_mu - rf) / portfolio_sigma
                │
                ▼
        run_simulation(portfolio_data)
                │
                └── SimulationConfig(tickers, weights, mu, sigma, corr,
                │                    initial_capital, monthly_dca, projection_years, n_simulations)
                │
                ▼
        run_monte_carlo(cfg)
                │
                ├── port_mu = w @ mu
                ├── cov = outer(sigma, sigma) * corr
                ├── port_sigma = sqrt(w @ cov @ w)   (volatilidad del portafolio)
                │
                ├── Z = rng.standard_normal((n_sim, n_steps))    ← ruido blanco
                ├── drift = (port_mu - 0.5*port_sigma²) * dt
                ├── diffusion = port_sigma * sqrt(dt) * Z
                ├── log_returns = drift + diffusion
                ├── cum_returns = exp(cumsum(log_returns))       ← paths normalizados
                ├── paths = initial_capital * cum_returns
                │
                ├── [si DCA > 0]: por cada mes, aporta monthly_dca y crece con el activo
                │
                ├── final_values = paths[:, -1]
                ├── percentiles: P5, P10, P25, P50, P75, P90, P95
                │
                └── _compute_metrics(result)
                    ├── expected_capital = mean(final)
                    ├── median_capital = median(final)
                    ├── var_95_value = percentile(final, 5)
                    ├── var_95_loss = total_invested - var_95_value
                    ├── cvar_95 = mean(final <= var_95_value)
                    ├── max_drawdown = min(drawdown de la mediana)
                    ├── prob_loss = mean(final < total_invested)
                    └── cagr_median = (median/initial)^(1/years) - 1
```

---

## Motor Financiero

### Optimización de Markowitz (`core/finance/markowitz.py`)

**Problema:** Encontrar pesos `w` que maximicen el ratio de Sharpe o minimicen la varianza.

```
Maximizar Sharpe:  max  (wᵀμ - rf) / √(wᵀΣw)
Minimizar Varianza: min  wᵀΣw
Sujeto a:           Σwᵢ = 1,  0.05 ≤ wᵢ ≤ 1.0
```

Usa `scipy.optimize.minimize` con método **SLSQP** (Sequential Least Squares Programming).

**Frontera Eficiente:** Barre retornos target desde `min(mu)` hasta `max(mu)` en 60 puntos, minimizando varianza para cada target.

**Retorna:** `OptimizationResult(weights, expected_return, volatility, sharpe_ratio, tickers, method)`

### Simulación Monte Carlo — GBM (`core/finance/monte_carlo.py`)

**Geometric Brownian Motion** para cada activo:

```
dS/S = μ dt + σ dW
S(t+dt) = S(t) · exp((μ - σ²/2)dt + σ·√dt·Z),   Z ~ N(0,1)
```

Se simula el portafolio como un solo proceso GBM usando:
- **Drift del portafolio:** `μ_p = wᵀμ`
- **Varianza del portafolio:** `σ²_p = wᵀ(outer(σ,σ) ⊙ C)w` donde C = matriz de correlación
- **Correlaciones preservadas** via descomposición de una sola variable: la volatilidad del portafolio captura las correlaciones

**DCA (Dollar Cost Averaging):** En cada paso mensual, se añade `monthly_dca` y se escala por el crecimiento futuro del portafolio desde ese punto.

**Retorna:** `SimulationResult(paths, final_values, config, percentiles, metrics)`

### Métricas de Riesgo (8)

| Métrica | Fórmula | Interpretación |
|---|---|---|
| **Capital Esperado** | `mean(final_values)` | Promedio de todos los escenarios |
| **Capital Mediano** | `median(final_values)` | Escenario del 50% percentil (referencia principal) |
| **VaR 95%** | `percentile(final_values, 5)` | En el 95% de casos, tu capital ≥ este valor |
| **Pérdida VaR** | `total_invested - var_95_value` | Pérdida potencial en dólares en el peor 5% |
| **CVaR 95%** | `mean(final_values ≤ var_95_value)` | Pérdida promedio en el peor 5% (Expected Shortfall) |
| **Max Drawdown** | `min((mediana - cummax) / cummax)` | Peor caída desde pico a valle en la trayectoria mediana |
| **Prob. Pérdida** | `mean(final_values < total_invested)` | Probabilidad de no recuperar lo invertido |
| **CAGR Mediano** | `(median_capital / initial)^(1/years) - 1` | Tasa de crecimiento anual compuesta del escenario mediano |

---

## Estructuras de Datos (SI210)

### 1. Cola FIFO — `DownloadQueue` (`core/ds/queue.py`)
**Unidad VII.** Lista enlazada simple. Se usa en `core/market/downloader.py` para encolar tickers y procesarlos secuencialmente.

```
enqueue(A) → enqueue(B) → enqueue(C)
Front → [A|→] → [B|→] → [C|None] ← Rear
dequeue() → A
```

| Método | Complejidad | Descripción |
|---|---|---|
| `enqueue(item)` | O(1) | Agrega al final (rear) |
| `dequeue()` | O(1) | Remueve del frente (front) |
| `peek()` | O(1) | Retorna frente sin remover |
| `is_empty()` | O(1) | Verifica si `front is None` |
| `clear()` | O(n) | Vacía la cola |
| `size` | O(1) | Propiedad con contador interno |

### 2. Pila LIFO — `SimulationStack` (`core/ds/stack.py`)
**Unidad VI.** Lista doblemente enlazada. Se usa en `ui/pages/simulator.py` para navegar entre simulaciones.

```
push(A) → push(B) → push(C)
None ← [A|⇄|B|⇄|C] → None
pop() → C
```

| Método | Complejidad | Descripción |
|---|---|---|
| `push(item)` | O(1) | Apila al tope |
| `pop()` | O(1) | Desapila del tope |
| `peek()` | O(1) | Tope sin eliminar |
| `is_empty()` | O(1) | Verifica si `top is None` |
| `clear()` | O(n) | Vacía la pila |
| `items()` | O(n) | Lista ordenada del tope al fondo |
| `size` | O(1) | Propiedad con contador interno |

### 3. Ordenamiento — `SimulationSorter` (`core/ds/sorting.py`)
**Unidad VIII.** Estrategia híbrida: QuickSort para n > 10, MergeSort para n ≤ 10.

| Método | Complejidad | Estable | Descripción |
|---|---|---|---|
| `merge_sort(items, key, reverse)` | O(n log n) | ✅ Sí | Divide y vencerás, merge estable |
| `quick_sort(items, key, reverse)` | O(n log n) promedio, O(n²) peor | ❌ No | Partición por pivote (último elemento) |
| `sort(items, key, reverse)` | O(n log n) | Depende | Elige según tamaño: n > 10 → QuickSort, else → MergeSort |

**Key function:** Soporta `callable`, `str` con notación de puntos (`"summary.median_capital"` para dicts anidados), o nombres de atributos.

### 4. Recorrido Recursivo de Árbol — `AssetCategoryTree` (`core/ds/tree_traversal.py`)
**Unidad II.** Árbol N-ario de categorías de activos con 3 niveles: raíz → categorías → tickers.

```
Todos los Activos (50)
├── 📁 Acciones USA - Tecnología (10)
│   ├── 📈 AAPL — Apple Inc.
│   ├── 📈 MSFT — Microsoft Corp.
│   └── ...
├── 📁 Acciones USA - Finanzas (5)
├── 📁 Acciones USA - Salud & Consumo (7)
├── 📁 Acciones USA - Energía & Industrial (5)
├── 📁 ETFs - Renta Variable (10)
├── 📁 ETFs - Renta Fija & Bonos (7)
├── 📁 Commodities & Alternativos (5)
└── 📁 Tecnología & Innovación (5)
```

| Método | Descripción |
|---|---|
| `traverse_preorder(node, depth, result)` | Raíz → hijos recursivamente (pre-order). Retorna `[{line, depth, name, is_leaf, data}]` con íconos por tipo |
| `traverse_postorder(node, depth, result)` | Hijos → raíz (post-order). Retorna `[str]` |
| `find_by_ticker(ticker, node)` | Búsqueda recursiva por ticker. Retorna `AssetTreeNode` o `None` |

### 5. Manejo de Cadenas — `StringValidator` (`core/utils/string_validator.py`)
**Unidad IV.** Validación con expresiones regulares.

| Método | Patrón | Reglas |
|---|---|---|
| `validate_email(email)` | `^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$` | No vacío, ≤ 254 chars |
| `validate_password(password)` | — | 8-128 caracteres |
| `validate_username(username)` | `^[a-zA-Z0-9_]+$` | 3-30 chars, alfanumérico + guión bajo |
| `validate_ticker(ticker)` / `sanitize_ticker(ticker)` | `^[A-Z]{1,5}$` | 1-5 letras mayúsculas, limpia y normaliza |

### 6. Jerarquía de Excepciones — `SmartRiskError` (`core/exceptions.py`)
**Unidad I.**

```
SmartRiskError(Exception)
├── AuthError(code="AUTH_ERROR")        — Login duplicado, credenciales inválidas
├── ValidationError(code="VALIDATION_ERROR") — Email, password, username inválidos
├── DataError(code="DATA_ERROR")        — JSON corrupto, error de E/S
└── SimulationError(code="SIMULATION_ERROR") — Parámetros inválidos en simulación
```

Todas tienen `__init__(message, code)` y `__str__` → `[CODE] message`.

### 7. Tipos Abstractos de Datos (TAD)

| Clase | Archivo | Propiedades Computadas |
|---|---|---|
| `PortfolioData` | `services/portfolio_service.py` | `portfolio_mu` (wᵀμ), `portfolio_sigma` (√(wᵀΣw)), `portfolio_sharpe` ((μ-rf)/σ), `risk_profile_check(profile) → dict` |
| `OptimizationResult` | `core/finance/markowitz.py` | Dataclass: weights, expected_return, volatility, sharpe_ratio, tickers, method |
| `SimulationConfig` | `core/finance/monte_carlo.py` | Dataclass: tickers, weights, mu_vec, sigma_vec, corr_matrix, initial_capital, monthly_dca, projection_years, n_simulations, dt, seed |
| `SimulationResult` | `core/finance/monte_carlo.py` | Dataclass: paths, final_values, config, percentiles, metrics |

---

## Capa de Persistencia (`database/repositories.py`)

### Estrategia

- **Formato:** JSON plano (archivos `.json`)
- **Sharding:** Un archivo por usuario por entidad (`data/users/{uuid}.json`, `data/portfolios/{uuid}.json`, etc.)
- **Escritura atómica:** Escribe a `.tmp` → `os.replace(tmp, path)` para evitar corrupción
- **Errores:** `DataError` con código `DATA_ERROR` en fallos de lectura/escritura
- **IDs:** UUID v4 (`uuid.uuid4()`)
- **Fechas:** ISO 8601 en UTC

### Esquemas JSON

**Usuario (`data/users/{id}.json`):**
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "password_hash": "bcrypt_hash",
  "role": "user|admin",
  "full_name": "string",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "is_active": true
}
```

**Portafolio (`data/portfolios/{id}.json`):**
```json
{
  "portfolios": {
    "{portfolio_id}": {
      "id": "uuid",
      "user_id": "uuid",
      "name": "string",
      "assets": ["ticker1", "ticker2"],
      "weights": [0.6, 0.4],
      "created_at": "ISO8601",
      "updated_at": "ISO8601"
    }
  }
}
```

**Simulación (`data/simulations/{id}.json`):**
```json
{
  "simulations": {
    "{sim_id}": {
      "id": "uuid",
      "user_id": "uuid",
      "config": {
        "tickers": ["AAPL", "MSFT"],
        "weights": [0.6, 0.4],
        "initial_capital": 10000,
        "monthly_dca": 0,
        "projection_years": 5,
        "n_simulations": 5000
      },
      "summary": {
        "expected_capital": 15000.0,
        "median_capital": 14200.0,
        "var_95_value": 8500.0,
        "var_95_loss": 1500.0,
        "cvar_95": 7800.0,
        "max_drawdown": -0.25,
        "prob_loss": 0.12,
        "cagr_median": 0.07,
        "total_invested": 10000.0
      },
      "created_at": "ISO8601"
    }
  }
}
```

**Resultado de Riesgo (`data/risk_results/{id}.json`):**
```json
{
  "user_id": "uuid",
  "profile": "conservador|moderado|agresivo",
  "score": 8,
  "answers": [1, 2, 3, 1, 2],
  "created_at": "ISO8601"
}
```

**Caché de Precios (`data/cache/{ticker}_{years}y.json`):**
```json
{
  "dates": ["2024-01-01", "2024-01-02"],
  "prices": [100.5, 101.2],
  "cached_at": "2024-06-01T12:00:00"
}
```

---

## Pipelines de Datos — Conexión entre Conceptos

### Pipeline 1: Registro de Usuario (Unidad IV → Unidad IX → Unidad I → Unidad XI → Sesión)

```
StringValidator.validate_username()      ← Unidad IV: validación de cadena (regex + 3-30 chars)
StringValidator.validate_email()         ← Unidad IV: validación de cadena (regex + ≤254 chars)
StringValidator.validate_password()      ← Unidad IV: validación de cadena (longitud 8-128)
    │   Si alguna falla → raise ValidationError   ← Unidad I: excepción personalizada
    ▼  (cadenas validadas y limpias)
hash_password(plain_password)            ← Unidad IX: hashing bcrypt (12 rounds) sobre bytes
    ▼  (hash almacenable: str de 60 chars)
create_user(username, email, hashed_password)
    │   _write() con tmp + os.replace()   ← Unidad XI: escritura atómica de archivos
    │   Si falla → raise DataError        ← Unidad I: excepción personalizada
    ▼  (JSON persistido)
login_session(user)                      ← Sesión en st.session_state
```

📌 **Archivo:** `auth/auth_service.py:16-52` — las 4 unidades trabajan en cadena en una sola función.

### Pipeline 2: Descarga de Precios (Unidad VII → Unidad XI → Unidad III)

```
DownloadQueue.enqueue(ticker) para cada ticker    ← Unidad VII: cola FIFO (lista enlazada simple)
    ▼
while not queue.is_empty():
    ticker = DownloadQueue.dequeue()              ← Unidad VII: desencola en orden FIFO
        │
        ├── _is_cache_valid(path)?               ← Unidad XI: verifica TTL del caché (6h)
        │   ├── Sí → _load_cache(path)            ← Unidad XI: lectura JSON
        │   └── No → yfinance.download() → _save_cache()  ← Unidad XI: escritura JSON
        ▼
    result[ticker] = precios (pd.Series)
    ▼
_compute_returns() → compute_stats()              ← Unidad III: vectores μ, σ como np.ndarray
build_correlation_matrix()                       ← Unidad III: matriz de correlación (2D)
```

📌 **Archivo:** `core/market/downloader.py:80-109` — `download_multiple()` usa `DownloadQueue`, caché JSON, y produce vectores/matrices NumPy.

### Pipeline 3: Navegación entre Simulaciones (Unidad VI → Sesión)

```
render_simulator()
    │
    ├── run_simulation() → result
    │       ▼
    ├── stack = st.session_state["sim_stack"]     ← Sesión: persiste la pila entre reruns
    │   stack.push((result, ...))                 ← Unidad VI: SimulationStack.push()
    │   st.session_state.sim_redo = SimulationStack()  ← Pila auxiliar para "Recuperar"
    │
    └── mostrar resultados desde stack.peek()     ← Unidad VI: SimulationStack.peek()

Botón "⏪ Descartar última"  → redo.push(stack.pop())   ← Unidad VI: pop() desapila, push() guarda en redo
Botón "Recuperar ⏩"        → stack.push(redo.pop())   ← Unidad VI: recupera desde redo
Botón "🗑️ Vaciar historial" → stack.clear() + redo.clear()
```

📌 **Archivo:** `ui/pages/simulator.py:187-233` — `SimulationStack` como pila LIFO con lista doblemente enlazada, persistida en `st.session_state`.

### Pipeline 4: Ordenamiento de Resultados (Unidad VIII → UI)

```
results.py
    │
    ├── selectbox("Ordenar por", ["Capital", "VAR95%", "CAGR"])
    │       ▼
    ├── sort_key = SORT_OPTIONS[selected_sort]    ← "summary.median_capital"
    │   _sort_key_fn(s) = _extract_value(s, "summary.median_capital")  ← notación de puntos
    │       ▼
    ├── SimulationSorter.sort(simulations, key=_sort_key_fn, reverse=True)
    │       │
    │       ├── ¿len(items) > 10?
    │       │   ├── Sí → QuickSort   ← Unidad VIII: O(n log n) promedio
    │       │   └── No  → MergeSort  ← Unidad VIII: O(n log n) estable
    │       ▼
    └── DataFrame(rows) → st.dataframe()
        │
        ├── Fila 0 = Mejor escenario (🏆)
        └── Fila -1 = Peor escenario (⚠️)
```

📌 **Archivo:** `ui/pages/results.py:56-119` — `SimulationSorter.sort()` con threshold automático QuickSort/MergeSort.

### Pipeline 5: Construcción del Árbol de Activos (Unidad II → UI)

```
config/assets.json
    │   (50 activos en 7 categorías)
    ▼
AssetCategoryTree(assets_data)
    │   _build(): por cada categoría → AssetTreeNode(categoría) → hijos AssetTreeNode(ticker)
    ▼
tree.traverse_preorder()
    │   Recorrido recursivo pre-order:
    │   ┌── 📂 Todos los Activos (50)
    │   │   ├── 📁 Acciones USA - Tecnología (10)
    │   │   │   ├── 📈 AAPL — Apple Inc.
    │   │   │   ├── 📈 MSFT — Microsoft Corp.
    │   │   │   └── ...
    │   │   ├── 📁 ETFs - Renta Variable (10)
    │   │   └── ...
    │   Retorna [{line, depth, name, is_leaf, data}] ← Unidad II: recursividad
    ▼
st.markdown(entry["line"]) para cada entry        ← UI: renderiza el árbol expandible
st.caption("📌 AssetCategoryTree.traverse_preorder() — recorrido recursivo pre-order")
```

📌 **Archivo:** `ui/pages/portfolio_builder.py:40-50` — árbol N-ario construido desde JSON, recorrido recursivo pre-order.

### Pipeline 6: Validación Tickers (Unidad IV → UI)

```
portfolio_builder.py
    │
    ├── st.multiselect() → selected_tickers
    │       ▼
    ├── for t in selected_tickers:
    │   is_valid, msg = StringValidator.validate_ticker(t)  ← Unidad IV: regex ^[A-Z]{1,5}$
    │   if not is_valid → alert_box()                       ← UI: muestra advertencia
    │
    ▼  (tickers validados)
build_portfolio_data(tickers, weights) → PortfolioData
```

📌 **Archivo:** `ui/pages/portfolio_builder.py:82-88` — validación de tickers antes de descargar datos.

### Pipeline 7: Optimización Markowitz (Unidad III → servicios → UI)

```
build_portfolio_data()
    │   _download_prices() → compute_stats() → build_correlation_matrix()
    ▼
PortfolioData(tickers, weights, prices, stats, returns, corr)
    │   .mu_vec     = np.array([stats[t]["mu"] for t in tickers])       ← Unidad III: vector
    │   .sigma_vec  = np.array([stats[t]["sigma"] for t in tickers])    ← Unidad III: vector
    │   .corr_array = corr_matrix.values                                 ← Unidad III: matriz 2D
    ▼
run_markowitz_optimization(portfolio_data, method)
    │   cov = np.outer(sigma, sigma) * corr                             ← Unidad III: matriz de covarianza
    │   maximize: (wᵀμ - rf) / √(wᵀΣw)                                 ← Unidad III: operaciones vectoriales
    ▼
OptimizationResult(weights, expected_return, volatility, sharpe_ratio)
    ▼
st.button("Maximizar Sharpe") / st.button("Minimizar Riesgo")
    │   on_click → st.rerun() → recarga con pesos optimizados
    ▼
st.number_input() para cada peso, actualizado con resultado
```

📌 **Archivo:** `ui/pages/portfolio_builder.py:106-124` + `services/portfolio_service.py` — optimización SLQSP sobre vectores/matrices NumPy.

### Pipeline 8: Persistencia con Manejo de Errores (Unidad XI → Unidad I)

```
repositories.py
    │
    ├── _read(filepath)
    │   │   open(path) → json.load()
    │   │   Si JSONDecodeError → raise DataError("Corrupted JSON file")  ← Unidad I
    │   │   Si OSError → raise DataError("Cannot read file")             ← Unidad I
    │
    ├── _write(filepath, data)
    │   │   json.dump() → tmp file → os.replace(tmp, path)              ← Unidad XI: escritura atómica
    │   │   Si OSError → raise DataError("Cannot write file")            ← Unidad I
    │
    └── Cada función CRUD (create_user, save_portfolio, etc.) usa _read/_write
            ▼
        UI captura SmartRiskError → st.error() muestra mensaje
```

📌 **Archivo:** `database/repositories.py:23-45` — `_read()` y `_write()` atómicos con `DataError` ante fallos de E/S.

---

## UI Components API

### `ui/components/metrics_cards.py`

```python
metric_card(label: str, value: str, delta: str = "", color: str = "#1B3A6B")
# Tarjeta métrica con label, valor grande, delta opcional, color personalizable

alert_box(message: str, alert_type: str = "info")
# Caja de alerta con 4 tipos: "info" (azul), "warning" (amarillo), "danger" (rojo), "success" (verde)

tooltip_box(text: str)
# Caja educativa azul claro con ícono 💡

section_header(title: str, subtitle: str = "")
# Título de sección con línea inferior azul claro

page_header(title: str, subtitle: str = "")
# Título de página grande con subtítulo gris

spacer(height: int = 1)
# Espaciador vertical en rem
```

### `ui/components/charts.py`

```python
plot_monte_carlo_paths(paths: np.ndarray, projection_years: float, initial_capital: float) -> go.Figure
# 7 líneas: mediana (negra, gruesa), 3 mejores (verdes), 3 peores (rojas). Línea punteada de capital inicial.
# Layout: título, ejes USD, leyenda horizontal abajo, 460px altura.

plot_final_value_histogram(final_values: np.ndarray, initial_capital: float) -> go.Figure
# Histograma con 60 bins. Líneas verticales: mediana (navy), VaR 95% (rojo), capital inicial (gris).
# 360px altura.

plot_portfolio_weights(tickers: list[str], weights: list[float]) -> go.Figure
# Gráfico de dona con 55% hole. Colores navy, blue, light-blue, green, orange. 320px altura.

plot_historical_performance(prices_dict: dict, weights: list[float], tickers: list[str]) -> go.Figure
# Líneas normalizadas a base 100. Cada ticker en color. Portafolio ponderado en rojo grueso. 380px altura.

```

### `ui/components/sidebar.py`

```python
render_sidebar()
# Renderiza: logo con imagen, nombre de usuario, rol (Inversor/Administrador),
# botones de navegación (6 páginas + 1 admin), botón de cerrar sesión.
# Botón activo = type="primary", inactivo = "secondary".
```

---

## Seguridad

- **Contraseñas:** Hasheadas con **bcrypt** (12 rounds) en `auth/password_utils.py`. Nunca almacenadas en texto plano.
- **Sesiones:** Uso de `st.session_state` con limpieza completa en `logout_session()`. No hay cookies ni JWT.
- **Escritura Atómica:** `os.replace(tmp, path)` previene corrupción de archivos JSON ante cortes de energía.
- **Validación de Entrada:** `StringValidator` en todos los formularios: registro (email, password, username), cambio de contraseña, tickers en constructor de portafolio, admin panel.
- **Jerarquía de Errores:** `SmartRiskError` capturada en UI con mensajes descriptivos. Los errores `DataError` y `SimulationError` tienen códigos específicos.
- **Admin Gate:** `render_admin_panel()` verifica `is_admin()` antes de renderizar. Redirección por session_state.
- **Streamlit:** Server headless, CORS deshabilitado solo en desarrollo.

---

## Instalación y Ejecución

```bash
# 1. Clonar
git clone <repo-url> smartrisk
cd smartrisk

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate        # macOS / Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
streamlit run app.py
```

**Credenciales por defecto:** `admin` / `Admin1234!` (se crea automáticamente al primer inicio).

---

## Guía de Usuario

### Flujo de Trabajo (4 Pasos)

```
1. Perfil de Riesgo ← 5 preguntas → Conservador / Moderado / Agresivo
        │
2. Constructor de Portafolio
   ├── Explora 50 activos en 7 categorías (árbol recursivo)
   ├── Selecciona hasta 5 activos
   ├── Asigna pesos (debe sumar 100%)
   ├── Normaliza automáticamente al cambiar selección
   ├── Optimiza con Markowitz: Maximizar Sharpe o Minimizar Riesgo
   └── Guarda portafolio
        │
3. Simulador Monte Carlo
   ├── Selecciona portafolio guardado
   ├── Configura: capital inicial, DCA, ventana histórica, proyección, N simulaciones
   ├── Descarga datos (cola FIFO + barra de progreso)
   ├── Recibe alerta si el portafolio excede la volatilidad del perfil
   ├── Ejecuta simulación GBM
   └── Navega entre simulaciones (pila LIFO: Descartar última / Recuperar)
        │
4. Resultados
   ├── Historial completo ordenable por Capital, VaR 95%, CAGR
   ├── Mejor/Peor escenario destacado
   └── Eliminación de simulaciones
```

### Páginas

| Página | Acceso | Función |
|---|---|---|
| Login/Registro | Público | Autenticación o creación de cuenta |
| Dashboard | Usuario | Checklist de 4 pasos, resumen de perfil, últimas simulaciones |
| Perfil de Riesgo | Usuario | Quiz de 5 preguntas → clasificación |
| Mi Portafolio | Usuario | Constructor con árbol + optimización + guardado |
| Simulador | Usuario | Monte Carlo con parámetros configurables |
| Resultados | Usuario | Historial ordenable |
| Panel Admin | Admin | CRUD de usuarios |
| Mi Cuenta | Usuario | Datos personales, cambio de contraseña, estadísticas |

---

## Guía de Desarrollo

### Cómo Agregar un Nuevo Activo

Editar `config/assets.json` — agregar a una categoría existente o crear una nueva:

```json
{
  "categories": {
    "Mi Nueva Categoría": [
      {"ticker": "NEW", "name": "Nuevo Activo", "type": "stock"}
    ]
  }
}
```

Tipos disponibles: `stock`, `etf`, `bond_etf`, `commodity_etf`, `reit`. El ícono se asigna en `tree_traversal.py` y `portfolio_builder.py`.

### Cómo Agregar un Nuevo Perfil de Riesgo

Editar `config/risk_profiles.json` y `config/risk_quiz.py` (umbral de clasificación en `classify_profile()`).

### Cómo Agregar una Nueva Métrica

1. Agregar cálculo en `_compute_metrics()` en `core/finance/monte_carlo.py`
2. Agregar visualización en `ui/pages/simulator.py` (fila de métricas) y `ui/pages/results.py` (columna ordenable)
3. Si se persiste, la métrica se guarda automáticamente en `summary`

### Cómo Agregar una Nueva Página

1. Crear `ui/pages/nueva_pagina.py` con función `render_nueva_pagina()`
2. Agregar a `PAGE_MAP` en `app.py`
3. Agregar botón de navegación en `NAV_ITEMS_USER` o `NAV_ITEMS_ADMIN` en `sidebar.py`

---

## Mapeo de Contenidos del Sílabo SI210 vs Implementación

| Unidad | Concepto del Sílabo | Implementación en SmartRisk | Archivo |
|---|---|---|---|
| **I** | Tipos Abstractos de Datos (TAD) | `PortfolioData`, `SimulationConfig`, `SimulationResult`, `OptimizationResult` | `services/portfolio_service.py`, `core/finance/markowitz.py`, `core/finance/monte_carlo.py` |
| **I** | Eventos / Excepciones | Jerarquía `SmartRiskError` → 4 subclases con `code` | `core/exceptions.py` |
| **II** | Recursividad | `AssetCategoryTree._build()`, `traverse_preorder()`, `traverse_postorder()`, `find_by_ticker()` | `core/ds/tree_traversal.py` |
| **III** | Arreglos (Vectores) | `np.ndarray` para pesos, retornos, vectores μ/σ | `core/finance/markowitz.py`, `core/finance/monte_carlo.py` |
| **III** | Matrices (2D) | Matriz de covarianza (`np.outer`), matriz de correlación, operación `w @ cov @ w` | `core/finance/markowitz.py`, `core/market/downloader.py` |
| **IV** | Manejo de Cadenas | `StringValidator`: email (regex), password, username, ticker | `core/utils/string_validator.py` |
| **V** | Listas Enlazadas Simples | `_Node` (data, next) en `DownloadQueue` | `core/ds/queue.py` |
| **V** | Listas Doblemente Enlazadas | `_Node` (data, prev, next) en `SimulationStack` | `core/ds/stack.py` |
| **VI** | Pilas (Stack) | `SimulationStack`: push, pop, peek — historial LIFO en simulador | `core/ds/stack.py`, `ui/pages/simulator.py` |
| **VII** | Colas (Queue) | `DownloadQueue`: enqueue, dequeue — descarga FIFO de tickers | `core/ds/queue.py`, `core/market/downloader.py` |
| **VIII** | Técnicas de Ordenamiento | `SimulationSorter`: QuickSort (n>10) y MergeSort (n≤10) | `core/ds/sorting.py`, `ui/pages/results.py` |
| **IX** | Técnicas de Hashing | bcrypt (12 rounds), UUID v4 | `auth/password_utils.py`, `database/repositories.py` |
| **XI** | Archivos (Lectura/Escritura) | Persistencia JSON atómica (`tmp` + `os.replace`), `DataError` | `database/repositories.py` |
| **XI** | Archivos (Caché) | Caché de precios JSON con TTL de 6 horas | `core/market/downloader.py` |
| **XII** | Ciencia de Datos / Exp. Regulares | pandas, numpy, GBM Monte Carlo, regex en `StringValidator` | Múltiples archivos |

### POO (Programación Orientada a Objetos)

| Concepto POO | Implementación |
|---|---|
| **Clases** | `PortfolioData`, `StringValidator`, `SimulationStack`, `DownloadQueue`, `SimulationSorter`, `AssetCategoryTree`, `AssetTreeNode`, `_Node` (x2), y 4 dataclasses |
| **Herencia** | `SmartRiskError` → `AuthError`, `ValidationError`, `DataError`, `SimulationError` |
| **Encapsulación** | `PortfolioData` con propiedades (`@property`) que ocultan cálculos matriciales |
| **Dataclasses** | `OptimizationResult`, `SimulationConfig`, `SimulationResult` |
| **Métodos de clase** | `StringValidator.validate_email()`, `SimulationSorter.sort()` |
| **Composición** | `AssetCategoryTree` compone `AssetTreeNode`; `DownloadQueue`/`SimulationStack` componen `_Node` |
