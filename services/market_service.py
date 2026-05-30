"""
SmartRisk - Market Service
Provides asset catalog and risk profile data from config files.
"""
import json

from config.settings import CONFIG_DIR


def get_asset_catalog() -> dict:
    with open(CONFIG_DIR / "assets.json", encoding="utf-8") as f:
        return json.load(f)


def get_risk_profiles() -> dict:
    """Loads risk profiles from JSON file."""
    path = CONFIG_DIR / "risk_profiles.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def flat_asset_list(assets_data: dict) -> list[dict]:
    """Flatten categorized assets into a list."""
    flat = []
    for category, items in assets_data["categories"].items():
        for item in items:
            flat.append({**item, "category": category})
    return flat
