# 📉 SmartRisk — Robo-Advisor Académico

**Plataforma de simulación estocástica y asesoramiento financiero personal**

> Curso: Estructura de Datos SI210M1 · Grupo X3 · Semestre 1-2026  
> Docente: Infantas Soto Karem Esther  
> Integrantes: Diego Rodas Ugarte · Julianne Arriharan Bejarano · Josue Mercado Parada

---

## 🚀 Inicio Rápido

### 1. Clonar / descomprimir el proyecto

```bash
cd smartrisk
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación abrirá automáticamente en `http://localhost:8501`

---

## 🔐 Credenciales por defecto

| Rol           | Usuario  | Contraseña   |
|---------------|----------|--------------|
| Administrador | `admin`  | `Admin1234!` |

> El admin es creado automáticamente al primer inicio si no existe.

---

## 🗂️ Estructura del Proyecto

```
smartrisk/
├── app.py                        # Punto de entrada principal
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml               # Tema y configuración de Streamlit
│
├── config/
│   ├── settings.py               # Variables globales
│   ├── assets.json               # Catálogo de 50 activos financieros
│   └── risk_profiles.json        # Perfiles: conservador/moderado/agresivo
│
├── data/                         # Persistencia JSON (auto-generado)
│   ├── users.json
│   ├── portfolios.json
│   ├── simulations.json
│   ├── risk_results.json
│   └── cache/                    # Caché de precios de mercado
│
├── auth/
│   ├── auth_service.py           # Registro y autenticación
│   ├── login.py                  # UI de login/registro
│   ├── password_utils.py         # Hashing bcrypt
│   └── session_manager.py        # Sesiones con Streamlit
│
├── database/
│   └── repositories.py           # CRUD sobre archivos JSON
│
├── core/
│   ├── finance/
│   │   ├── monte_carlo.py        # Motor GBM + Cholesky
│   │   ├── markowitz.py          # Optimización Sharpe/MinVar
│   │   └── metrics.py            # VaR, CVaR, Sharpe, Sortino, etc.
│   ├── market/
│   │   └── downloader.py         # yfinance + caché local
│   └── utils/
│       ├── validators.py
│       └── formatters.py
│
├── services/
│   ├── portfolio_service.py      # Orquesta datos + optimización
│   ├── simulation_service.py     # Orquesta Monte Carlo
│   ├── market_service.py         # Consultas de mercado
│   └── user_service.py           # Operaciones sobre usuarios
│
├── ui/
│   ├── pages/
│   │   ├── dashboard.py          # Panel principal
│   │   ├── risk_quiz.py          # Quiz de perfil de riesgo
│   │   ├── portfolio_builder.py  # Constructor de cartera
│   │   ├── simulator.py          # Simulador Monte Carlo
│   │   ├── results.py            # Historial de simulaciones
│   │   ├── admin_panel.py        # Panel administrativo
│   │   └── profile.py            # Perfil de usuario
│   ├── components/
│   │   ├── sidebar.py            # Navegación lateral
│   │   ├── charts.py             # Gráficos Plotly
│   │   └── metrics_cards.py      # Cards, alertas, badges
│   └── styles/
│       └── custom_css.py         # CSS personalizado
│
└── tests/
    ├── test_monte_carlo.py
    ├── test_markowitz.py
    └── test_metrics.py
```

---

## ✨ Funcionalidades

### 🎯 Perfil de Riesgo
- Quiz interactivo de 5 preguntas
- Clasificación: Conservador · Moderado · Agresivo
- Auditoría automática cartera vs perfil

### 📊 Constructor de Portafolio
- Catálogo de 50 activos (acciones, ETFs, bonos, commodities)
- Hasta 5 activos con asignación por sliders
- Tickers personalizados (cualquier símbolo de Yahoo Finance)
- Guardado persistente en JSON

### 🔬 Simulación Monte Carlo
- Movimiento Browniano Geométrico (GBM)
- Descomposición de Cholesky para correlaciones reales
- 1.000 a 10.000 escenarios configurables
- DCA (aportaciones mensuales) opcional
- Ventana histórica: 1, 3, 5, 7 o 10 años

### 📈 Métricas de Riesgo
| Métrica | Descripción |
|---|---|
| Capital Final Mediano | Tendencia central del crecimiento |
| VaR 95% | Pérdida máxima probable |
| CVaR 95% | Pérdida esperada más allá del VaR |
| Max Drawdown | Peor caída proyectada |
| Sharpe Ratio | Eficiencia riesgo/retorno |
| Sortino Ratio | Sharpe penalizando solo volatilidad negativa |
| CAGR | Tasa de crecimiento anual compuesta |
| Prob. de Pérdida | % de escenarios que terminan en pérdida |

### 🎯 Optimización Markowitz
- Maximización del Ratio de Sharpe
- Minimización de la varianza
- Frontera eficiente interactiva (Plotly)
- Solver: SciPy SLSQP

### 🛠️ Panel Admin
- CRUD completo de usuarios
- Asignación de roles (admin/user)
- Estadísticas globales de la plataforma

---

## 🧪 Ejecutar Tests

```bash
pytest tests/ -v
```

Tests disponibles:
- `test_monte_carlo.py` — 15+ casos: GBM, métricas, DCA, Sharpe
- `test_markowitz.py`   — 12+ casos: pesos, métodos, frontera eficiente
- `test_metrics.py`     — 18+ casos: VaR, CVaR, Sharpe, Sortino, MDD

---

## 🌐 Deploy

### Streamlit Cloud
1. Subir el repositorio a GitHub
2. Ir a [share.streamlit.io](https://share.streamlit.io)
3. Conectar el repo, apuntar a `app.py`

### Render
1. Crear un nuevo Web Service
2. Build command: `pip install -r requirements.txt`
3. Start command: `streamlit run app.py --server.port $PORT --server.headless true`

---

## ⚙️ Stack Tecnológico

| Área | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| UI Framework | Streamlit |
| Persistencia | JSON (archivos locales) |
| Datos de Mercado | yfinance |
| Cálculo Numérico | NumPy |
| Optimización | SciPy (SLSQP) |
| DataFrames | Pandas |
| Visualizaciones | Plotly |
| Seguridad | bcrypt |
| Testing | pytest |

---

## 📝 Notas Académicas

- Todas las simulaciones son **proyecciones estadísticas**, no garantías financieras
- Los datos de mercado son históricos y no predicen rendimientos futuros
- Proyecto de carácter académico — no usar para inversiones reales
- Moneda base: **USD (Dólares Americanos)**
