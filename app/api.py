"""
Single API surface exposed to the frontend as `window.pywebview.api`.
Every method here is callable from JS. Methods return plain
dict/list/str/number/bool so PyWebView can serialize them automatically.
"""

import json
from datetime import datetime, timezone

import webview

from app.services import (
    chrome_service,
    news_service,
    project_service,
    revenue_service,
    settings_service,
    wallet_service,
)
from app.utils import paths as path_utils


class Api:
    # ---------------- Dashboard ----------------
    def get_dashboard(self):
        return {
            "total_revenue": revenue_service.total_revenue(),
            "upcoming_tge": project_service.list_upcoming_tge(),
        }

    # ---------------- Projects (Main / Secondary) ----------------
    def get_projects(self, list_type):
        return project_service.list_projects(list_type)

    def create_project(self, list_type, data):
        try:
            return {"success": True, "project": project_service.create_project(list_type, data)}
        except ValueError as exc:
            return {"success": False, "error": str(exc)}

    def update_project(self, project_id, data):
        try:
            return {"success": True, "project": project_service.update_project(project_id, data)}
        except ValueError as exc:
            return {"success": False, "error": str(exc)}

    def delete_project(self, project_id):
        try:
            project_service.delete_project(project_id)
            return {"success": True}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}

    def export_projects(self, list_type):
        try:
            window = webview.windows[0]
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            default_name = f"manager-airdrop-{list_type.lower()}-{timestamp}.json"
            result = window.create_file_dialog(
                webview.FileDialog.SAVE,
                directory=path_utils.get_default_export_dir(),
                save_filename=default_name,
                file_types=("JSON Files (*.json)", "All files (*.*)"),
            )
            if not result:
                return {"success": False}
            target = result if isinstance(result, str) else result[0]

            records = project_service.export_projects(list_type)
            with open(target, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
            return {"success": True, "path": target, "count": len(records)}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}

    def import_projects(self, list_type):
        try:
            window = webview.windows[0]
            result = window.create_file_dialog(
                webview.FileDialog.OPEN,
                directory=path_utils.get_default_export_dir(),
                file_types=("JSON Files (*.json)", "All files (*.*)"),
            )
            if not result:
                return {"success": False}
            source = result[0] if isinstance(result, (list, tuple)) else result

            with open(source, "r", encoding="utf-8") as f:
                records = json.load(f)
            if not isinstance(records, list):
                return {"success": False, "error": "File không đúng định dạng."}

            count = project_service.import_projects(list_type, records)
            return {"success": True, "count": count}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}

    def open_project_link(self, url):
        settings = settings_service.get_settings()
        return chrome_service.open_url(
            url,
            settings.get("chrome_user_data_path", ""),
            settings.get("chrome_profile_name", ""),
        )

    # ---------------- Wallets ----------------
    def get_wallets(self):
        return wallet_service.list_wallets()

    def create_wallet(self, data):
        try:
            return {"success": True, "wallet": wallet_service.create_wallet(data)}
        except ValueError as exc:
            return {"success": False, "error": str(exc)}

    def update_wallet(self, wallet_id, data):
        try:
            return {"success": True, "wallet": wallet_service.update_wallet(wallet_id, data)}
        except ValueError as exc:
            return {"success": False, "error": str(exc)}

    def delete_wallet(self, wallet_id):
        try:
            wallet_service.delete_wallet(wallet_id)
            return {"success": True}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}

    def copy_to_clipboard(self, text):
        try:
            import pyperclip

            pyperclip.copy(text or "")
            return {"success": True}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}

    # ---------------- Revenue ----------------
    def get_revenue(self):
        return {
            "records": revenue_service.list_revenue(),
            "total": revenue_service.total_revenue(),
        }

    def update_revenue(self, revenue_id, data):
        try:
            return {"success": True, "revenue": revenue_service.update_revenue(revenue_id, data)}
        except ValueError as exc:
            return {"success": False, "error": str(exc)}

    # ---------------- Check News ----------------
    def generate_news_prompt(self, scope, check_scope="NEWS"):
        return news_service.generate_prompt(scope, check_scope)

    # ---------------- Settings ----------------
    def get_settings(self):
        return settings_service.get_settings()

    def update_chrome_settings(self, chrome_user_data_path, chrome_profile_name):
        try:
            return {
                "success": True,
                "settings": settings_service.update_chrome_settings(
                    chrome_user_data_path, chrome_profile_name
                ),
            }
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}

    def update_app_data_path(self, new_path):
        try:
            return {"success": True, "settings": settings_service.update_app_data_path(new_path)}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}

    def browse_folder(self):
        try:
            window = webview.windows[0]
            result = window.create_file_dialog(webview.FileDialog.FOLDER)
            if result:
                return {"success": True, "path": result[0]}
            return {"success": False}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}
