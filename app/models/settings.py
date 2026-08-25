"""
Settings are stored as key-value rows in the `settings` table inside the
SQLite database (which itself lives at the configured App Data Path):

- chrome_user_data_path : str -- path to the Chrome "User Data" folder
- chrome_profile_name   : str -- e.g. "Default" or "Profile 1"

`app_data_path` is intentionally NOT stored here -- see
app/utils/paths.py for why it lives in app_config.json instead.
"""

DEFAULT_SETTINGS = {
    "chrome_user_data_path": "",
    "chrome_profile_name": "",
}
