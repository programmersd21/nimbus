"""
config.py — nimbus Configuration Manager
Loads/saves user config from %APPDATA%\\nimbus\\config.json
"""

import json
import logging
import os

log = logging.getLogger("nimbus.config")

CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "nimbus")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG: dict = {
    # Window
    "position_y": 12,  # Distance from top of screen (px)
    "opacity": 1.0,  # Global opacity (0.0 – 1.0)
    # Features
    "show_clock": True,
    "show_media": True,
    "show_notifications": True,
    # Visuals
    "theme": "dark",  # "dark" | "light" (future)
    "pill_blur": True,
    # Behavior
    "auto_collapse_ms": 3000,  # Auto-collapse after 3 seconds
}


def load_config() -> dict:
    """Load config, merging with defaults for any missing keys."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                data = json.load(f)
            return {**DEFAULT_CONFIG, **data}
        except Exception as e:
            log.warning("Could not load config (%s), using defaults.", e)
    return dict(DEFAULT_CONFIG)


def save_config(config: dict) -> None:
    """Persist config to disk."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        log.error("Could not save config: %s", e)
