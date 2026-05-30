# SmartRisk — Robo-Advisor Académico

**SmartRisk** es una plataforma de simulación financiera y asesoramiento automatizado de portafolios, desarrollada como proyecto final de la materia **SI210 — Estructura de Datos**. Implementa los conceptos fundamentales de la materia aplicados a un problema real: la construcción, optimización y simulación de portafolios de inversión.

> **Nota:** Todas las simulaciones son proyecciones estadísticas con fines académicos. No constituyen asesoría financiera ni garantizan rendimientos futuros.

---

## Mapeo de Contenidos del Sílabo SI210 vs Implementación

SmartRisk aplica los siguientes contenidos de la materia **Estructura de Datos (SI210)**:

| Unidad | Concepto del Sílabo | Implementación en SmartRisk |
|---|---|---|
| **I** | Tipos Abstractos de Datos (TAD) | `PortfolioData`, `SimulationConfig`, `SimulationResult`, `OptimizationResult` |
| **I** | Eventos / Excepciones | Jerarquía `SmartRiskError` → `AuthError`, `ValidationError`, `DataError` (persistencia), `SimulationError` (simulación) |
| **III** | Arreglos (Vectores) | `np.ndarray` para pesos, retornos, vectores de media/volatilidad |
| **III** | Matrices (2D) | Matriz de covarianza (`np.outer`), matriz de correlación (`DataFrame.corr()`), operaciones `w @ cov @ w` |
| **IV** | Manejo de Cadenas | `StringValidator`: validación de email (regex), username, contraseña, tickers |
| **V** | Listas Enlazadas Simples | `_Node` en `DownloadQueue` (FIFO con lista enlazada simple) |
| **V** | Listas Doblemente Enlazadas | `_Node` con `prev`/`next` en `SimulationStack` (pila LIFO con lista doblemente enlazada) |
| **VI** | Pilas (Stack) | `SimulationStack` — pila LIFO para historial de simulaciones en sesión (`push`, `pop`, `peek`) |
| **VII** | Colas (Queue) | `DownloadQueue` — cola FIFO para descarga secuencial de tickers (`enqueue`, `dequeue`) |
| **VIII** | Técnicas de Ordenamiento | `SimulationSorter` — QuickSort (n>10) y MergeSort (n≤10) para ordenar resultados |
| **IX** | Técnicas de Hashing | `bcrypt` para hash de contraseñas (12 rounds), `uuid4()` para IDs únicos |
| **XI** | Archivos (Lectura/Escritura) | Persistencia JSON atómica (`tmp` + `os.replace`), con `DataError` en fallos |
| **XI** | Archivos (Caché) | Caché de precios en JSON con TTL de 6 horas en `core/market/downloader.py` |
| **XII** | Ciencia de Datos / Expresiones Regulares | `pandas`, `numpy`, GBM Monte Carlo, regex para validación |

### POO (Programación Orientada a Objetos)

| Concepto POO | Implementación |
|---|---|
| **Clases** | `PortfolioData`, `StringValidator`, `SimulationStack`, `DownloadQueue`, `SimulationSorter`, `AssetCategoryTree`, y 4 dataclasses |
| **Herencia** | `SmartRiskError` → `AuthError`, `ValidationError`, `DataError`, `SimulationError` |
| **Encapsulación** | `PortfolioData` con propiedades (`@property`) que ocultan cálculos |
| **Dataclasses** | `OptimizationResult`, `SimulationConfig`, `SimulationResult` |

---

## Stack Tecnológico

| Área | Tecnología |
|---|---|
| Lenguaje | Python ≥ 3.11 |
| UI Framework | Streamlit |
| Datos de mercado | yfinance |
| Cálculo numérico | NumPy |
| Optimización | SciPy (SLSQP) |
| Manipulación de datos | Pandas |
| Visualizaciones | Plotly |
| Autenticación | bcrypt |
| Testing | pytest (157 tests) |
| Persistencia | JSON (sharded por usuario) |

---

## Instalación y Ejecución

```bash
# 1. Clonar el repositorio
git clone <repo-url> smartrisk
cd smartrisk

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate        # macOS / Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
streamlit run app.py
```

**Credenciales por defecto:** `admin` / `Admin1234!` (se crea automáticamente al primer inicio).

---

## Estructura del Proyecto

```
smartrisk/
├── app.py                              # Punto de entrada
├── requirements.txt                    # Dependencias
├── README.md
│
├── .streamlit/
│   └── config.toml                     # Tema visual + servidor
│
├── config/
│   ├── settings.py                     # Constantes globales
│   ├── assets.json                     # 50 activos en 7 categorías
│   └── risk_profiles.json              # 3 perfiles de riesgo
│
├── auth/
│   ├── auth_service.py                 # Registro y autenticación (usa StringValidator)
│   ├── login.py                        # UI de login y registro
│   ├── password_utils.py              # Hashing bcrypt (hash + verify)
│   └── session_manager.py             # Gestión de sesión
│
├── database/
│   └── repositories.py                # CRUD sobre JSON con DataError
│
├── core/
│   ├── ds/                             # 📌 Estructuras de Datos (proyecto)
│   │   ├── queue.py                    # DownloadQueue — Cola FIFO (lista enlazada simple)
│   │   ├── stack.py                    # SimulationStack — Pila LIFO (lista doblemente enlazada)
│   │   ├── sorting.py                  # SimulationSorter — QuickSort / MergeSort
│   │   └── tree_traversal.py          # AssetCategoryTree — Recorrido recursivo
│   ├── exceptions.py                   # Jerarquía SmartRiskError (5 clases)
│   ├── finance/
│   │   ├── markowitz.py               # Optimización Markowitz (SLSQP) + frontera eficiente
│   │   └── monte_carlo.py             # Motor GBM con DCA + SimulationError
│   ├── market/
│   │   └── downloader.py              # Descarga yfinance + caché JSON + DownloadQueue
│   └── utils/
│       └── string_validator.py         # StringValidator — validación de cadenas
│
├── services/
│   ├── portfolio_service.py           # PortfolioData + build_portfolio_data
│   ├── simulation_service.py          # Monte Carlo → persistencia
│   └── market_service.py              # Catálogo de activos y perfiles
│
├── ui/
│   ├── components/
│   │   ├── sidebar.py                 # Navegación lateral
│   │   ├── charts.py                  # 4 gráficos Plotly (proyección, distribución, histórico, correlaciones)
│   │   └── metrics_cards.py           # Cards, alertas, tooltips
│   ├── pages/
│   │   ├── dashboard.py               # Panel principal
│   │   ├── risk_quiz.py              # Quiz de perfil de riesgo
│   │   ├── portfolio_builder.py      # Constructor con árbol recursivo + validación
│   │   ├── simulator.py              # Simulador Monte Carlo + SimulationStack LIFO
│   │   ├── results.py                # Historial + SimulationSorter
│   │   ├── admin_panel.py            # CRUD de usuarios
│   │   └── profile.py                # Perfil de usuario
│   └── styles/
│       └── custom_css.py             # CSS personalizado
│
├── tests/
│   ├── test_ds.py                    # 30 tests: Queue, Stack, Sorter, Tree
│   ├── test_string_validator.py      # 21 tests: StringValidator
│   ├── test_auth.py                  # 16 tests: Auth y registro
│   ├── test_repositories.py          # 28 tests: CRUD sobre JSON
│   ├── test_markowitz.py             # 14 tests: Optimización
│   ├── test_monte_carlo.py           # 18 tests: Simulación GBM
│   ├── test_services.py              # 23 tests: Servicios
│   ├── test_integration.py           # 3 tests: Flujo completo
│   └── test_ui_smoke.py             # 4 tests: UI smoke
│
└── data/                              # Creado automáticamente al ejecutar
    ├── users/                         # JSON por usuario
    ├── portfolios/                    # JSON por usuario
    ├── simulations/                   # JSON por usuario
    ├── risk_results/                  # JSON por usuario
    └── cache/                         # Precios cacheados (TTL 6h)
```

---

## Implementación de Estructuras de Datos

### 1. Cola FIFO — `DownloadQueue` (`core/ds/queue.py`)

**Unidad VII del sílabo.** Cola FIFO con lista enlazada simple.

```python
class _Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class DownloadQueue:
    def enqueue(self, item)    # Agrega al final
    def dequeue(self)          # Quita del frente
    def is_empty(self)         # Verifica si está vacía
    @property
    def size(self)             # Tamaño de la cola
```

**Aplicación real:** En `core/market/downloader.py`, los tickers a descargar se encolan y procesan secuencialmente en orden FIFO. La UI muestra barra de progreso con indicador `📌 DownloadQueue (cola FIFO con lista enlazada simple)`.

---

### 2. Pila LIFO — `SimulationStack` (`core/ds/stack.py`)

**Unidad VI del sílabo.** Pila LIFO con lista doblemente enlazada.

```python
class _Node:
    def __init__(self, data, prev=None, next=None):
        self.data = data
        self.prev = prev
        self.next = next

class SimulationStack:
    def push(self, item)       # Apila al tope
    def pop(self)              # Desapila del tope
    def peek(self)             # Mira el tope sin eliminar
    @property
    def size(self)             # Tamaño de la pila
```

**Aplicación real:** En `ui/pages/simulator.py`, cada simulación ejecutada se apila. Navegación LIFO: "Descartar última" (pop) y "Recuperar" (redo). La UI muestra `📌 SimulationStack (pila LIFO con lista doblemente enlazada)`.

---

### 3. Ordenamiento — `SimulationSorter` (`core/ds/sorting.py`)

**Unidad VIII del sílabo.** MergeSort y QuickSort.

```python
class SimulationSorter:
    def merge_sort(items, key, reverse)    # O(n log n) — estable
    def quick_sort(items, key, reverse)    # O(n log n) promedio
    def sort(items, key, reverse)          # Elige según tamaño
```

**Aplicación real:** En `ui/pages/results.py`, ordena simulaciones por capital final, VaR, CAGR. QuickSort si >10 elementos, MergeSort si ≤10. La UI muestra `📌 SimulationSorter.sort() — QuickSort / MergeSort`.

---

### 4. Recorrido Recursivo de Árbol — `AssetCategoryTree` (`core/ds/tree_traversal.py`)

**Unidad II (Recursividad).** Árbol de categorías con recorrido recursivo pre-order.

```python
class AssetCategoryTree:
    def traverse_preorder(self)   # Recorrido recursivo pre-order
    def traverse_postorder(self)  # Recorrido recursivo post-order
    def find_by_ticker(self)      # Búsqueda recursiva
```

**Aplicación real:** En `ui/pages/portfolio_builder.py`, expander que muestra el árbol completo de categorías. La UI muestra `📌 AssetCategoryTree.traverse_preorder() — recorrido recursivo`.

---

### 5. Manejo de Cadenas — `StringValidator` (`core/utils/string_validator.py`)

**Unidad IV del sílabo.** Validación de strings con expresiones regulares.

```python
class StringValidator:
    def validate_email(email)        # Regex + longitud
    def validate_password(password)  # 8-128 caracteres
    def validate_username(username)  # 3-30, alfanumérico
    def validate_ticker(ticker)      # 1-5 letras mayúsculas
```

**Aplicación real:** Validación en registro (`auth_service.py`), cambio de contraseña (`admin_panel.py`, `profile.py`), y tickers (`portfolio_builder.py`).

---

### 6. Jerarquía de Excepciones — `SmartRiskError` (`core/exceptions.py`)

**Unidad I del sílabo.** Excepciones personalizadas con herencia.

```python
SmartRiskError
├── AuthError            # Error de autenticación (usuario duplicado, credenciales)
├── ValidationError      # Error de validación (email, password, username)
├── DataError            # Error de persistencia (lectura/escritura JSON)
└── SimulationError      # Error de simulación (parámetros inválidos)
```

**Aplicación real:** `AuthError`/`ValidationError` capturados en login y admin. `DataError` lanzado en `repositories.py` al fallar JSON. `SimulationError` lanzado en `monte_carlo.py` con parámetros inválidos.

---

### 7. Tipos Abstractos de Datos (TAD)

| Clase | Archivo | Propósito |
|---|---|---|
| `PortfolioData` | `services/portfolio_service.py` | Contenedor con propiedades computadas |
| `OptimizationResult` | `core/finance/markowitz.py` | Dataclass pesos, retorno, volatilidad, Sharpe |
| `SimulationConfig` | `core/finance/monte_carlo.py` | Dataclass parámetros de simulación |
| `SimulationResult` | `core/finance/monte_carlo.py` | Dataclass resultados y métricas |

---

### 8. Hashing

**Unidad IX del sílabo.** bcrypt (12 rounds) en `auth/password_utils.py`. UUID v4 en `database/repositories.py`.

---

### 9. Archivos / Persistencia

**Unidad XI del sílabo.** `_read()`/`_write()` atómicos con `os.replace()`. `DataError` en fallos de E/S. Sharding por usuario.

---

## Arquitectura y Flujo de Datos

```
Usuario → UI (Streamlit)
              │
              ▼
         auth/ → login / registro / sesión
              │
              ▼
         services/portfolio_service.py
              │  PortfolioData (TAD)
              │
              ├──► core/market/downloader.py
              │       DownloadQueue FIFO + caché JSON
              │
              ├──► core/finance/markowitz.py
              │       SLSQP → max_sharpe / min_variance
              │
              └──► core/finance/monte_carlo.py
                      GBM → simulation + métricas
                      SimulationStack LIFO → historial
                           │
                           ▼
                      database/repositories.py
                      JSON atómico → data/simulations/
                           │
                           ▼
                      ui/pages/simulator.py (4 tabs)
                      + results.py (SimulationSorter)
```

---

## Guía de Usuario

### Flujo de Trabajo

```
Registro / Login
       │
       ▼
   Dashboard
       │
       ▼
   Perfil de Riesgo   ← Quiz → Conservador / Moderado / Agresivo
       │
       ▼
   Constructor de     ← 50 activos en árbol recursivo
   Portafolio         → Asigna pesos / Normaliza / Optimiza Markowitz
       │
       ▼
   Simulador Monte    ← GBM con DCA, miles de escenarios
   Carlo              → 8 métricas + 4 gráficos
       │                Pila LIFO: navegación entre simulaciones
       ▼
   Resultados         ← Historial ordenable por métrica
                       → Mejor/Peor escenario destacado
```

### Páginas del Sistema

1. **Dashboard**: Checklist de 4 pasos, perfil de riesgo, últimas simulaciones.
2. **Perfil de Riesgo**: 5 preguntas → clasificación en Conservador/Moderado/Agresivo.
3. **Constructor de Portafolio**: Catálogo de 50 activos (árbol recursivo), pesos, optimización Markowitz, validación de tickers con `StringValidator`.
4. **Simulador Monte Carlo**: Descarga FIFO con cola, simulación GBM, pila LIFO de historial, 4 tabs de visualización (Proyección con mediana+3 best+3 worst, Distribución, Histórico, Correlaciones con análisis de diversificación).
5. **Resultados**: Historial con ordenamiento por `SimulationSorter` (QuickSort/MergeSort), mejor/peor escenario.
6. **Admin Panel**: CRUD de usuarios con validación centralizada (`StringValidator`).
7. **Perfil de Usuario**: Información, cambio de contraseña, estadísticas.

---

## Tests

```bash
pytest tests/ -v    # 157 tests
```

| Archivo | Tests | Cobertura |
|---|---|---|
| `test_ds.py` | 30 | Queue, Stack, Sorting, Tree |
| `test_string_validator.py` | 21 | Email, password, username, ticker |
| `test_auth.py` | 16 | Registro, autenticación |
| `test_repositories.py` | 28 | CRUD usuarios, portafolios, simulaciones |
| `test_markowitz.py` | 14 | Optimización, frontera eficiente |
| `test_monte_carlo.py` | 18 | GBM, DCA, percentiles |
| `test_services.py` | 23 | PortfolioData, simulación |
| `test_integration.py` | 3 | Flujo completo |
| `test_ui_smoke.py` | 4 | Carga de UI |

---

## Seguridad

- **Contraseñas**: hasheadas con bcrypt (12 rounds). Nunca en texto plano.
- **Sesiones**: `st.session_state` con limpieza completa al cerrar sesión.
- **Escritura atómica**: `os.replace()` para evitar corrupción de archivos.
- **Validación de entrada**: `StringValidator` en todo formulario (email, password, tickers).
- **Error handling**: Jerarquía `SmartRiskError` con `DataError` en persistencia y `SimulationError` en simulación.
