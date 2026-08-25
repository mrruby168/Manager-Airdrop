"""
Opens a project's Web Link in Chrome using the user-configured Chrome
Profile (APP_SPEC sections 6.2 and 10.2).
"""

import shutil
import subprocess
from pathlib import Path

COMMON_CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def _find_chrome_executable() -> str:
    for path in COMMON_CHROME_PATHS:
        if Path(path).exists():
            return path
    found = shutil.which("chrome") or shutil.which("google-chrome") or shutil.which("chromium")
    if found:
        return found
    raise FileNotFoundError(
        "Không tìm thấy Chrome trên máy. Vui lòng cài đặt Google Chrome."
    )


def open_url(url: str, chrome_user_data_path: str, chrome_profile_name: str) -> dict:
    if not url:
        return {"success": False, "error": "Web Link trống."}
    try:
        chrome_path = _find_chrome_executable()
        args = [chrome_path]
        if chrome_user_data_path:
            args.append(f"--user-data-dir={chrome_user_data_path}")
        if chrome_profile_name:
            args.append(f"--profile-directory={chrome_profile_name}")
        args.append(url)
        subprocess.Popen(args)
        return {"success": True}
    except Exception as exc:  # noqa: BLE001 - surfaced to UI as Error State
        return {"success": False, "error": str(exc)}
