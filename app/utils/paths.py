"""
Path and configuration helpers.

The database itself can live in a user-configured location (Settings ->
App Data Path). Because that setting determines *where the database is*,
it cannot be stored inside the database. Instead it is kept in a small
bootstrap file (``app_config.json``) that always lives next to ``main.py``,
so the app can find its data on every launch regardless of where the user
pointed it.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "app_config.json"
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
DB_FILENAME = "manager_airdrop.db"


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_config(config: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_app_data_path() -> Path:
    config = load_config()
    path_str = config.get("app_data_path")
    if path_str:
        return Path(path_str)
    return DEFAULT_DATA_DIR


def set_app_data_path(new_path: str) -> None:
    config = load_config()
    config["app_data_path"] = str(new_path)
    save_config(config)


def get_db_path() -> Path:
    data_dir = get_app_data_path()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / DB_FILENAME


# Default folder pre-filled in the Import / Export project data dialogs.
DEFAULT_EXPORT_DIR = r"C:\Users\mrrub\Downloads"


def get_default_export_dir() -> str:
    return DEFAULT_EXPORT_DIR
