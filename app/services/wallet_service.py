from datetime import datetime, timezone

from app.database.db import get_cursor
from app.models.wallet import Wallet


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def list_wallets() -> list:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM wallets ORDER BY created_at DESC")
        return [Wallet.from_row(r).to_dict() for r in cur.fetchall()]


def create_wallet(data: dict) -> dict:
    name = (data.get("name") or "").strip()
    address = (data.get("address") or "").strip()
    if not name or not address:
        raise ValueError("Tên ví và Địa chỉ là bắt buộc.")

    now = _now()
    with get_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO wallets (name, address, note, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (name, address, (data.get("note") or "").strip(), now, now),
        )
        new_id = cur.lastrowid
    with get_cursor() as cur:
        cur.execute("SELECT * FROM wallets WHERE id = ?", (new_id,))
        return Wallet.from_row(cur.fetchone()).to_dict()


def update_wallet(wallet_id: int, data: dict) -> dict:
    with get_cursor() as cur:
        cur.execute("SELECT * FROM wallets WHERE id = ?", (wallet_id,))
        row = cur.fetchone()
    if row is None:
        raise ValueError("Không tìm thấy ví.")
    existing = Wallet.from_row(row)

    name = (data.get("name", existing.name) or "").strip()
    address = (data.get("address", existing.address) or "").strip()
    if not name or not address:
        raise ValueError("Tên ví và Địa chỉ là bắt buộc.")

    now = _now()
    with get_cursor(commit=True) as cur:
        cur.execute(
            "UPDATE wallets SET name=?, address=?, note=?, updated_at=? WHERE id=?",
            (name, address, (data.get("note", existing.note) or "").strip(), now, wallet_id),
        )
        cur.execute("SELECT * FROM wallets WHERE id = ?", (wallet_id,))
        return Wallet.from_row(cur.fetchone()).to_dict()


def delete_wallet(wallet_id: int) -> None:
    with get_cursor(commit=True) as cur:
        cur.execute("DELETE FROM wallets WHERE id = ?", (wallet_id,))
