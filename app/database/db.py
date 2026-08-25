"""
SQLite connection management and schema initialization.

Schema follows APP_SPEC.md sections 11 (Project Data), 12 (Wallet Table),
13 (Revenue Table) and 14 (Settings Data).

Note: `event_date` on `projects` is a minimal necessary addition beyond the
field list in APP_SPEC section 11.1. The spec's own Dashboard/Upcoming TGE
examples (section 5) display a concrete date per project ("ABC — TGE ngay
30/08/2026"), which requires a date to be stored somewhere. This field
holds that date (used for TGE display and as the default Revenue date).
See README.md "Assumptions" for details.
"""

import sqlite3
from contextlib import contextmanager

from app.utils.paths import get_db_path

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    web_link TEXT,
    x_handle TEXT,
    status TEXT NOT NULL DEFAULT 'ONLINE' CHECK(status IN ('TGE','CLAIMED','ONLINE')),
    note TEXT,
    list_type TEXT NOT NULL CHECK(list_type IN ('MAIN','SECONDARY')),
    event_date TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    note TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS revenue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    project_name TEXT NOT NULL,
    amount REAL NOT NULL DEFAULT 0,
    date TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_projects_list_type ON projects(list_type);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_revenue_project_id ON revenue(project_id);
"""

_connection = None


def get_connection():
    """Return the singleton SQLite connection, creating/initializing it
    (and its parent folder) on first use."""
    global _connection
    if _connection is None:
        db_path = get_db_path()
        _connection = sqlite3.connect(str(db_path), check_same_thread=False)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA foreign_keys = ON")
        # WAL keeps reads/writes fast and non-blocking as the local database
        # grows over long-term use; NORMAL sync is the recommended pairing.
        _connection.execute("PRAGMA journal_mode = WAL")
        _connection.execute("PRAGMA synchronous = NORMAL")
        _connection.executescript(SCHEMA)
        _connection.commit()
    return _connection


def reset_connection() -> None:
    """Close the current connection. Used when the App Data Path changes
    so the next call to get_connection() opens the database at the new
    location."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None


@contextmanager
def get_cursor(commit: bool = False):
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
        if commit:
            conn.commit()
    finally:
        cur.close()
