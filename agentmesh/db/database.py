import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".agentmesh" / "agentmesh.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS messages (
                id          TEXT PRIMARY KEY,
                thread_id   TEXT NOT NULL,
                sender_id   TEXT NOT NULL,
                recipient_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                body        TEXT NOT NULL,
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at  TEXT NOT NULL,
                read        INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS agent_memory (
                id          TEXT PRIMARY KEY,
                agent_id    TEXT NOT NULL,
                memory_type TEXT NOT NULL CHECK(memory_type IN ('short', 'long')),
                content     TEXT NOT NULL,
                created_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS agent_states (
                agent_id    TEXT PRIMARY KEY,
                state       TEXT NOT NULL,
                updated_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id          TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                submitted_by TEXT NOT NULL DEFAULT 'human',
                status      TEXT NOT NULL DEFAULT 'pending',
                created_at  TEXT NOT NULL,
                completed_at TEXT
            );

            CREATE TABLE IF NOT EXISTS events (
                id          TEXT PRIMARY KEY,
                session_id  TEXT NOT NULL,
                event_type  TEXT NOT NULL,
                actor_id    TEXT NOT NULL,
                payload_json TEXT NOT NULL DEFAULT '{}',
                created_at  TEXT NOT NULL
            );
        """)
