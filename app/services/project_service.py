"""
Project service. Backs both Main List and Secondary List (APP_SPEC
sections 6 and 7), differentiated by `list_type` ('MAIN' / 'SECONDARY').
"""

from datetime import datetime, timezone

from app.database.db import get_cursor
from app.models.project import VALID_LIST_TYPES, VALID_STATUSES, Project
from app.services import revenue_service


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _validate_list_type(list_type: str) -> None:
    if list_type not in VALID_LIST_TYPES:
        raise ValueError(f"list_type không hợp lệ: {list_type}")


def _validate(list_type: str, status: str) -> None:
    _validate_list_type(list_type)
    if status not in VALID_STATUSES:
        raise ValueError(f"status không hợp lệ: {status}")


def list_projects(list_type: str) -> list:
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM projects WHERE list_type = ? ORDER BY created_at DESC",
            (list_type,),
        )
        return [Project.from_row(r).to_dict() for r in cur.fetchall()]


def get_project(project_id: int):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cur.fetchone()
        return Project.from_row(row).to_dict() if row else None


def create_project(list_type: str, data: dict) -> dict:
    name = (data.get("name") or "").strip()
    if not name:
        raise ValueError("Tên dự án là bắt buộc.")
    status = data.get("status", "ONLINE")
    _validate(list_type, status)

    now = _now()
    with get_cursor(commit=True) as cur:
        cur.execute(
            """INSERT INTO projects
               (name, web_link, x_handle, status, note, list_type, event_date, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                name,
                (data.get("web_link") or "").strip(),
                (data.get("x_handle") or "").strip(),
                status,
                (data.get("note") or "").strip(),
                list_type,
                (data.get("event_date") or "").strip(),
                now,
                now,
            ),
        )
        new_id = cur.lastrowid

    project = get_project(new_id)
    revenue_service.sync_for_project(project)
    return project


def update_project(project_id: int, data: dict) -> dict:
    existing = get_project(project_id)
    if not existing:
        raise ValueError("Không tìm thấy dự án.")

    name = (data.get("name", existing["name"]) or "").strip()
    if not name:
        raise ValueError("Tên dự án là bắt buộc.")
    status = data.get("status", existing["status"])
    _validate(existing["list_type"], status)

    now = _now()
    with get_cursor(commit=True) as cur:
        cur.execute(
            """UPDATE projects SET name=?, web_link=?, x_handle=?, status=?,
               note=?, event_date=?, updated_at=? WHERE id=?""",
            (
                name,
                (data.get("web_link", existing["web_link"]) or "").strip(),
                (data.get("x_handle", existing["x_handle"]) or "").strip(),
                status,
                (data.get("note", existing["note"]) or "").strip(),
                (data.get("event_date", existing["event_date"]) or "").strip(),
                now,
                project_id,
            ),
        )

    project = get_project(project_id)
    revenue_service.sync_for_project(project)
    return project


def delete_project(project_id: int) -> None:
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM revenue WHERE project_id = ?", (project_id,))
        cur.execute("DELETE FROM projects WHERE id = ?", (project_id,))


def export_projects(list_type: str) -> list:
    """Return a JSON-serializable list of project records for `list_type`,
    for the Import / Export project data feature."""
    _validate_list_type(list_type)
    projects = list_projects(list_type)
    return [
        {
            "name": p["name"],
            "web_link": p["web_link"],
            "x_handle": p["x_handle"],
            "status": p["status"],
            "note": p["note"],
            "event_date": p["event_date"],
        }
        for p in projects
    ]


def import_projects(list_type: str, records: list) -> int:
    """Create projects in `list_type` from previously exported records.
    Invalid records (e.g. missing name) are skipped instead of aborting
    the whole import. Returns the number of projects created."""
    _validate_list_type(list_type)
    imported = 0
    for data in records or []:
        if not isinstance(data, dict):
            continue
        try:
            create_project(list_type, data)
            imported += 1
        except ValueError:
            continue
    return imported


def list_upcoming_tge() -> list:
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM projects WHERE status = 'TGE' "
            "ORDER BY (event_date = '') ASC, event_date ASC, created_at ASC"
        )
        return [Project.from_row(r).to_dict() for r in cur.fetchall()]
