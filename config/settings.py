"""
SmartRisk - Global Configuration Settings
"""
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
EXPORTS_DIR = DATA_DIR / "exports"
CONFIG_DIR = BASE_DIR / "config"

# JSON persistence files
USERS_FILE = DATA_DIR / "users.json"
PORTFOLIOS_FILE = DATA_DIR / "portfolios.json"
SIMULATIONS_FILE = DATA_DIR / "simulations.json"
RISK_RESULTS_FILE = DATA_DIR / "risk_results.json"

# ── App Meta ───────────────────────────────────────────────────────────────────
APP_NAME = "SmartRisk"
APP_VERSION = "1.0.0"

# ── Simulation Defaults ────────────────────────────────────────────────────────
DEFAULT_SIMULATIONS = 5000
MAX_SIMULATIONS = 15000
DEFAULT_INITIAL_CAPITAL = 10000
DEFAULT_MONTHLY_DCA = 0
DEFAULT_PROJECTION_YEARS = 5
DEFAULT_HISTORY_YEARS = 5
RISK_FREE_RATE = 0.035  # 3.5% annual (US T-bill proxy)

# ── Portfolio Constraints ──────────────────────────────────────────────────────
MAX_ASSETS = 5
MIN_WEIGHT = 0.05
MAX_WEIGHT = 1.0

# ── Market Data ────────────────────────────────────────────────────────────────
CACHE_EXPIRY_HOURS = 6
MAX_HISTORY_YEARS = 10

# ── Roles ─────────────────────────────────────────────────────────────────────
ROLE_ADMIN = "admin"


