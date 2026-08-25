"""
Manager Airdrop - application entry point.

Starts the Python process, initializes the local SQLite database, and
opens the PyWebView window loading the local HTML/CSS/JS UI. No HTTP
server or backend API is used, per APP_SPEC.md section 1.5.
"""

import webview

from app.api import Api
from app.database.db import get_connection


def main():
    # Make sure the database (and its data folder) exists before the UI loads.
    get_connection()

    api = Api()
    webview.create_window(
        "Manager Airdrop",
        "app/ui/index.html",
        js_api=api,
        width=1280,
        height=800,
        min_size=(1024, 640),
        background_color="#0B0E14",
    )
    webview.start()


if __name__ == "__main__":
    main()
