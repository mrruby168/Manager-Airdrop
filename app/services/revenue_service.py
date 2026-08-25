"""
Revenue service.

APP_SPEC section 9.1: when a project's status becomes CLAIMED, it must be
"brought into" the Revenue list. This module keeps a revenue record in
sync with each project's status automatically:

- status -> CLAIMED      : ensure a revenue record exists (amount starts
                            at 0; the user fills in the real amount from
                            the Revenue tab).
- status CLAIMED -> other: remove the associated revenue record, since it
                            is no longer a claimed/realized project.

The revenue record's `amount` and `date` remain user-editable via
update_revenue(), matching APP_SPEC 9.2's Revenue UI (Project Name,
Revenue, Date).
"""

from datetime import datetime, timezone

from app.database.db import get_cursor
from app.models.revenue import Revenue


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sync_for_project(project: dict) -> None:
    if project is None:
        return

    with get_cursor() as cur:
        cur.execute("SELECT id FROM revenue WHERE project_id = ?", (project["id"],))
        existing = cur.fetchone()

    if project["status"] == "CLAIMED":
        if existing is None:
            now = _now()
            default_date = project.get("event_date") or now[:10]
            with get_cursor(commit=True) as cur:
                cur.execute(
                    """INSERT INTO revenue
                       (project_id, project_name, amount, date, created_at, updated_at)
                       VALUES (?, ?, 0, ?, ?, ?)""",
                    (project["id"], project["name"], default_date, now, now),
                )
        else:
            with get_cursor(commit=True) as cur:
                cur.execute(
                    "UPDATE revenue SET project_name = ?, updated_at = ? WHERE project_id = ?",
                    (project["name"], _now(), project["id"]),
                )
    else:
        if existing is not None:
            with get_cursor(commit=True) as cur:
                cur.execute("DELETE FROM revenue WHERE project_id = ?", (project["id"],))


def list_revenue() -> list:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM revenue ORDER BY date DESC, created_at DESC")
        return [Revenue.from_row(r).to_dict() for r in cur.fetchall()]


def update_revenue(revenue_id: int, data: dict) -> dict:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM revenue WHERE id = ?", (revenue_id,))
        row = cur.fetchone()
    if row is None:
        raise ValueError("Không tìm thấy bản ghi Revenue.")

    existing = Revenue.from_row(row)
    amount = data.get("amount", existing.amount)
    date = data.get("date", existing.date)
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise ValueError("Doanh thu phải là một số.")

    now = _now()
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE revenue SET amount = ?, date = ?, updated_at = ? WHERE id = ?",
            (amount, date, now, revenue_id),
        )
        cur.execute("SELECT * FROM revenue WHERE id = ?", (revenue_id,))
        updated = cur.fetchone()
    return Revenue.from_row(updated).to_dict()


def total_revenue() -> float:
    with get_cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM revenue")
        row = cur.fetchone()
        return round(row["total"] or 0, 2)
