# SmartRisk — Robo-Advisor Académico

**SmartRisk** es una plataforma de simulación financiera y asesoramiento automatizado de portafolios, desarrollada como proyecto final de la materia **SI210 — Estructura de Datos**. Implementa los conceptos fundamentales de la materia aplicados a un problema real: la construcción, optimización y simulación de portafolios de inversión.

> **Nota:** Todas las simulaciones son proyecciones estadísticas con fines académicos. No constituyen asesoría financiera ni garantizan rendimientos futuros.

---

## Mapeo de Contenidos del Sílabo SI210 vs Implementación

SmartRisk aplica los siguientes contenidos de la materia **Estructura de Datos (SI210)**:

| Unidad | Concepto del Sílabo | Implementación en SmartRisk |
|---|---|---|
| **I** | Tipos Abstractos de Datos (TAD) | `PortfolioData`, `SimulationConfig`, `SimulationResult`, `OptimizationResult` |
| **I** | Eventos / Excepciones | Jerarquía `SmartRiskError` → `AuthError`, `ValidationError`, `DataError`, `SimulationError` |
| **III** | Arreglos (Vectores) | `np.ndarray` para pesos, retornos, vectores de media/volatilidad |
| **III** | Matrices (2D) | Matriz de covarianza (`np.outer`), matriz de correlación (`DataFrame.corr()`), operaciones `w @ cov @ w` |
| **IV** | Manejo de Cadenas | `StringValidator`: validación de email (regex), username, contraseña, tickers |
| **V** | Listas Enlazadas Simples | `_Node` en `DownloadQueue` (FIFO con lista enlazada simple) |
| **V** | Listas Doblemente Enlazadas | `_Node` con `prev`/`next` en `SimulationStack` (pila LIFO con lista doblemente enlazada) |
| **VI** | Pilas (Stack) | `SimulationStack` — pila LIFO para historial de simulaciones en sesión (`push`, `pop`, `peek`) |
| **VII** | Colas (Queue) | `DownloadQueue` — cola FIFO para descarga secuencial de tickers (`enqueue`, `dequeue`) |
| **VIII** | Técnicas de Ordenamiento | `SimulationSorter` — QuickSort y MergeSort para ordenar resultados de simulación |
| **IX** | Técnicas de Hashing | `bcrypt` para hash de contraseñas (12 rounds), `uuid4()` para IDs únicos |
| **XI** | Archivos (Lectura/Escritura) | Persistencia JSON en `database/repositories.py` con escritura atómica (`tmp` + `os.replace`) |
| **XI** | Archivos (Caché) | Caché de precios en JSON con TTL de 6 horas en `core/market/downloader.py` |
| **XII** | Ciencia de Datos / Expresiones Regulares | `pandas`, `numpy`, regex para validación de email |

### POO (Programación Orientada a Objetos)

| Concepto POO | Implementación |
|---|---|
| **Clases** | `PortfolioData`, `StringValidator`, `SimulationStack`, `DownloadQueue`, `SimulationSorter`, `AssetCategoryTree`, `AssetTreeNode`, y 4 dataclasses |
| **Herencia** | `AuthError(SmartRiskError)`, `ValidationError(SmartRiskError)`, `DataError(SmartRiskError)`, `SimulationError(SmartRiskError)` |
| **Encapsulación** | `PortfolioData` con propiedades (`@property`) que ocultan cálculos internos |
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
| Testing | pytest (179 tests) |
| Persistencia | JSON (4 archivos sharded por usuario) |

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
│   ├── auth_service.py                 # Registro y autenticación
│   ├── login.py                        # UI de login y registro
│   ├── password_utils.py              # Hashing bcrypt (hash + verify)
│   └── session_manager.py             # Gestión de sesión
│
├── database/
│   └── repositories.py                # CRUD sobre JSON sharded por usuario
│
├── core/
│   ├── ds/                             # 📌 Estructuras de Datos (proyecto)
│   │   ├── queue.py                    # DownloadQueue — Cola FIFO (lista enlazada simple)
│   │   ├── stack.py                    # SimulationStack — Pila LIFO (lista doblemente enlazada)
│   │   ├── sorting.py                  # SimulationSorter — QuickSort / MergeSort
│   │   └── tree_traversal.py          # AssetCategoryTree — Recorrido recursivo (pre-order / post-order)
│   ├── exceptions.py                   # Jerarquía SmartRiskError
│   ├── finance/
│   │   ├── metrics.py                  # Sharpe, Sortino, VaR, CVaR, Max Drawdown, Calmar
│   │   ├── markowitz.py               # Optimización Markowitz (SLSQP) + frontera eficiente
│   │   └── monte_carlo.py             # Motor GBM con DCA
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
│   │   ├── charts.py                  # 6 gráficos Plotly
│   │   └── metrics_cards.py           # Cards, alertas, tooltips
│   ├── pages/
│   │   ├── dashboard.py               # Panel principal
│   │   ├── risk_quiz.py              # Quiz de perfil de riesgo
│   │   ├── portfolio_builder.py      # Constructor con pesos y optimización
│   │   ├── simulator.py              # Simulador Monte Carlo + SimulationStack
│   │   ├── results.py                # Historial + SimulationSorter
│   │   ├── admin_panel.py            # CRUD de usuarios
│   │   └── profile.py                # Perfil de usuario
│   └── styles/
│       └── custom_css.py             # CSS personalizado
│
├── tests/
│   ├── test_ds.py                    # 30 tests: Queue, Stack, Sorter, Tree
│   ├── test_string_validator.py      # 14 tests: StringValidator
│   ├── test_auth.py                  # 16 tests: Auth y registro
│   ├── test_repositories.py          # 29 tests: CRUD sobre JSON
│   ├── test_metrics.py               # 22 tests: Métricas financieras
│   ├── test_markowitz.py             # 14 tests: Optimización
│   ├── test_monte_carlo.py           # 17 tests: Simulación GBM
│   ├── test_services.py              # 24 tests: Servicios
│   ├── test_integration.py           # 3 tests: Flujo completo
│   └── test_ui_smoke.py             # 4 tests: UI smoke
│
└── data/                              # Creado automáticamente al ejecutar
    ├── users/                         # JSON por usuario
    ├── portfolios/                    # JSON por usuario
    ├── simulations/                   # JSON por usuario
    ├── risk_results/                  # JSON por usuario
    ├── cache/                         # Precios cacheados (TTL 6h)
    └── exports/                       # CSVs descargados
```

---

## Implementación de Estructuras de Datos

### 1. Cola FIFO — `DownloadQueue` (`core/ds/queue.py`)

**Unidad VII del sílabo.** Implementación de una cola (FIFO) usando lista enlazada simple.

```python
class _Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class DownloadQueue:
    def enqueue(self, item)    # Agrega al final
    def dequeue(self)          # Quita del frente
    def peek(self)             # Mira el frente sin eliminar
    def is_empty(self)         # Verifica si está vacía
```

**Aplicación real:** En `core/market/downloader.py`, los tickers a descargar se encolan y se procesan secuencialmente en orden FIFO, con barra de progreso en la UI.

**Defensa:** "Cada ticker se pone en una cola y se procesa en el orden que llegó — igual que una fila de banco, pero para descargar datos de mercado."

---

### 2. Pila LIFO — `SimulationStack` (`core/ds/stack.py`)

**Unidad VI del sílabo.** Implementación de una pila (LIFO) usando lista doblemente enlazada.

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
    def items(self)            # Retorna todos desde el tope
```

**Aplicación real:** En `ui/pages/simulator.py`, cada simulación ejecutada se apila. El usuario puede "Descartar última" (pop) o "Recuperar" (push desde redo stack). Se muestra el tamaño de la pila.

**Defensa:** "Cada simulación se apila. La última en entrar es la primera en mostrarse. Si descartas, haces pop — LIFO puro."

---

### 3. Ordenamiento — `SimulationSorter` (`core/ds/sorting.py`)

**Unidad VIII del sílabo.** Implementación de MergeSort y QuickSort.

```python
class SimulationSorter:
    def merge_sort(items, key, reverse)    # O(n log n) — estable
    def quick_sort(items, key, reverse)    # O(n log n) promedio
    def sort(items, key, reverse)          # Elige algoritmo según tamaño
```

**Aplicación real:** En `ui/pages/results.py`, las simulaciones guardadas pueden ordenarse por capital final, VaR, CAGR, etc. El algoritmo se selecciona automáticamente: QuickSort para más de 10 elementos, MergeSort para menos.

**Defensa:** "Podemos ordenar las simulaciones por mejor capital o peor VaR con QuickSort o MergeSort, dependiendo de la cantidad de elementos."

---

### 4. Recorrido Recursivo de Árbol — `AssetCategoryTree` (`core/ds/tree_traversal.py`)

**Unidad II (Recursividad) y Unidad I (Árboles) del sílabo.** Construcción de un árbol de categorías de activos y recorrido recursivo pre-order y post-order.

```python
class AssetTreeNode:
    def __init__(self, name, children, data):
        self.name = name
        self.children = children
        self.data = data

class AssetCategoryTree:
    def traverse_preorder(self)   # Recorrido recursivo pre-order
    def traverse_postorder(self)  # Recorrido recursivo post-order
    def find_by_ticker(self)      # Búsqueda recursiva
```

**Aplicación real:** En `ui/pages/portfolio_builder.py`, se muestra un expander con el árbol completo de categorías de activos, generado mediante recorrido recursivo pre-order.

**Defensa:** "Los activos están organizados en un árbol de categorías. Usamos recursividad para recorrerlo en pre-order y mostrarlo al usuario."

---

### 5. Manejo de Cadenas — `StringValidator` (`core/utils/string_validator.py`)

**Unidad IV del sílabo.** Operaciones de validación y manipulación de strings.

```python
class StringValidator:
    def validate_email(email)        # Regex + longitud
    def validate_password(password)  # Longitud mínima/máxima
    def validate_username(username)  # Caracteres permitidos + longitud
    def sanitize_ticker(ticker)      # Limpieza y validación de tickers
    def validate_ticker(ticker)      # Validación completa
```

**Aplicación real:** En `auth/auth_service.py` para validar registro de usuarios. En `ui/pages/portfolio_builder.py` para validar tickers seleccionados.

**Defensa:** "Cada entrada de usuario pasa por validación de cadenas: email con regex, contraseña con longitud mínima, tickers con formato estricto."

---

### 6. Jerarquía de Excepciones — `SmartRiskError` (`core/exceptions.py`)

**Unidad I del sílabo (Eventos/Excepciones).** Jerarquía de excepciones personalizadas con herencia.

```python
SmartRiskError           # Base — todas heredan de esta
├── AuthError            # Errores de autenticación
├── ValidationError      # Errores de validación de entrada
├── DataError            # Errores de persistencia
└── SimulationError      # Errores de simulación
```

**Aplicación real:** Captura específica de errores en `auth_service.py`, `login.py`, `admin_panel.py`. Cada excepción tiene un código único (`[AUTH_ERROR]`, `[VALIDATION_ERROR]`).

**Defensa:** "Tenemos una jerarquía de herencia de 5 niveles. Cada tipo de error se captura por separado para dar mensajes precisos al usuario."

---

### 7. Tipos Abstractos de Datos (TAD)

**Unidad I del sílabo.** Clases que encapsulan datos y operaciones.

| Clase | Archivo | Propósito |
|---|---|---|
| `PortfolioData` | `services/portfolio_service.py` | Contenedor con propiedades computadas (`@property`) |
| `OptimizationResult` | `core/finance/markowitz.py` | Dataclass con pesos, retorno, volatilidad, Sharpe |
| `SimulationConfig` | `core/finance/monte_carlo.py` | Dataclass con parámetros de simulación |
| `SimulationResult` | `core/finance/monte_carlo.py` | Dataclass con resultados, percentiles y métricas |

**Defensa:** "Cada TAD encapsula sus datos y expone métodos para operar sobre ellos, ocultando la complejidad interna."

---

### 8. Hashing

**Unidad IX del sílabo.** Implementado mediante:

- **bcrypt** (`auth/password_utils.py`): Hash de contraseñas con 12 rounds de sal. Cada hash es único aunque la contraseña sea la misma.
- **UUID v4** (`database/repositories.py`): Identificadores únicos universales para usuarios, portafolios, simulaciones.

**Defensa:** "Las contraseñas se almacenan con hash bcrypt — aunque dos usuarios tengan la misma contraseña, sus hashes son distintos por la sal aleatoria. Los IDs son UUIDs que garantizan unicidad global."

---

### 9. Archivos / Persistencia

**Unidad XI del sílabo.** Sistema completo de lectura y escritura de archivos JSON:

- **Lectura**: `_read(filepath)` con manejo de `JSONDecodeError`
- **Escritura atómica**: `_write(filepath, data)` escribe a `.tmp` y luego hace `os.replace()` (operación atómica en Windows)
- **Sharding**: Cada usuario tiene su propio archivo JSON para portafolios, simulaciones y perfil de riesgo
- **Caché**: Precios de mercado cacheados en JSON con TTL de 6 horas

**Defensa:** "Los datos persisten en archivos JSON. La escritura atómica evita corrupción ante cortes de energía. Cada usuario tiene sus propios archivos (sharding), lo que permite escalar sin base de datos."

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
              │  properties: mu, sigma, sharpe
              │
              ├──► core/market/downloader.py
              │       DownloadQueue → descarga FIFO + caché JSON
              │
              ├──► core/finance/markowitz.py
              │       SLSQP → max_sharpe / min_variance
              │
              └──► core/finance/monte_carlo.py
                      GBM → simulation + métricas
                      SimulationStack → historial LIFO
                           │
                           ▼
                      database/repositories.py
                      JSON write atómico → data/simulations/
                           │
                           ▼
                      ui/pages/simulator.py
                      + results.py (SimulationSorter → ordenamiento)
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
   Constructor de     ← Selecciona activos, asigna pesos
   Portafolio         → Normaliza / Optimiza (Markowitz)
       │
       ▼
   Simulador Monte    ← GBM con DCA, miles de escenarios
   Carlo              → 8 métricas + 5 gráficos
       │                Pila LIFO: navega entre simulaciones
       ▼
   Resultados         ← Historial ordenable por métrica
                       → Mejor / Peor escenario destacado
```

### Páginas del Sistema

1. **Dashboard**: Resumen con checklist de 4 pasos, perfil de riesgo, últimas simulaciones.
2. **Perfil de Riesgo**: 5 preguntas → puntaje 5-15 → clasificación en Conservador/Moderado/Agresivo.
3. **Constructor de Portafolio**: Catálogo de 50 activos, asignación de pesos, normalización, optimización Markowitz, árbol recursivo de categorías.
4. **Simulador Monte Carlo**: Configuración de parámetros, descarga FIFO con barra de progreso, simulación GBM, pila LIFO de historial de sesión, 5 pestañas de visualización, exportación CSV.
5. **Resultados**: Historial de simulaciones con ordenamiento por métrica (QuickSort/MergeSort), mejor/peor escenario destacados, comparación lado a lado.
6. **Admin Panel**: CRUD de usuarios, métricas globales.
7. **Perfil de Usuario**: Información personal, cambio de contraseña, estadísticas.

---

## Tests

```bash
pytest tests/ -v    # 179 tests
```

| Archivo | Tests | Cobertura |
|---|---|---|
| `test_ds.py` | 30 | Queue, Stack, Sorting, Tree |
| `test_string_validator.py` | 14 | Email, password, username, ticker |
| `test_auth.py` | 16 | Registro, autenticación |
| `test_repositories.py` | 29 | CRUD usuarios, portafolios, simulaciones |
| `test_metrics.py` | 22 | Sharpe, Sortino, VaR, CVaR, Drawdown |
| `test_markowitz.py` | 14 | Optimización, frontera eficiente |
| `test_monte_carlo.py` | 17 | GBM, DCA, percentiles |
| `test_services.py` | 24 | PortfolioData, simulación |
| `test_integration.py` | 3 | Flujo completo |
| `test_ui_smoke.py` | 4 | Carga de UI |

---

## Seguridad

- **Contraseñas**: hasheadas con bcrypt (12 rounds). Nunca en texto plano.
- **Sesiones**: `st.session_state` con limpieza completa al cerrar sesión.
- **Escritura atómica**: `os.replace()` para evitar corrupción de archivos.
- **Validación de entrada**: `StringValidator` en registro (email regex, username, password).
- **Error handling**: Barrera `try/except` global + jerarquía de excepciones personalizadas.
