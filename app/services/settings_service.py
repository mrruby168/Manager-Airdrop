"""
Settings service (APP_SPEC section 10). Handles Chrome Profile config and
the App Data Path, including safely relocating the SQLite database when
the App Data Path changes (existing data is preserved, never deleted).
"""

import shutil
from pathlib import Path

from app.database.db import get_cursor, reset_connection
from app.models.settings import DEFAULT_SETTINGS
from app.utils import paths as path_utils


def get_settings() -> dict:
    with get_cursor() as cur:
        cur.execute("SELECT key, value FROM settings")
        rows = {r["key"]: r["value"] for r in cur.fetchall()}
    settings = dict(DEFAULT_SETTINGS)
    settings.update(rows)
    settings["app_data_path"] = str(path_utils.get_app_data_path())
    return settings


def update_chrome_settings(chrome_user_data_path: str, chrome_profile_name: str) -> dict:
    with get_cursor(commit=True) as cur:
        for key, value in (
            ("chrome_user_data_path", (chrome_user_data_path or "").strip()),
            ("chrome_profile_name", (chrome_profile_name or "").strip()),
        ):
            cur.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )
    return get_settings()


def update_app_data_path(new_path: str) -> dict:
    """Point the app at a new data folder, copying the existing database
    over (if any) so no data is lost. Old data is never deleted."""
    new_path = (new_path or "").strip()
    if not new_path:
        raise ValueError("Đường dẫn không hợp lệ.")

    new_dir = Path(new_path)
    new_dir.mkdir(parents=True, exist_ok=True)

    old_db = path_utils.get_db_path()
    reset_connection()

    path_utils.set_app_data_path(str(new_dir))
    new_db = path_utils.get_db_path()

    if old_db.exists() and old_db != new_db and not new_db.exists():
        shutil.copy2(old_db, new_db)

    return get_settings()
