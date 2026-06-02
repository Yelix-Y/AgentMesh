import json
import uuid
from enum import Enum
from datetime import datetime, timezone
from typing import Any

from agentmesh.db.database import get_connection


class EventType(str, Enum):
    SESSION_STARTED = "session_started"
    SESSION_QUIESCENT = "session_quiescent"
    SESSION_MAX_STEPS = "session_max_steps"
    SESSION_FAILED = "session_failed"
    MESSAGE_PUBLISHED = "message_published"
    MESSAGE_IGNORED = "message_ignored"


class EventLog:
    """Append-only log of everything that happens in a session, so a run can be
    audited and replayed."""

    def record(
        self,
        session_id: str,
        event_type: EventType | str,
        actor_id: str,
        payload: dict[str, Any] | None = None,
    ) -> str:
        event_id = str(uuid.uuid4())
        event_value = event_type.value if isinstance(event_type, EventType) else event_type
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO events (id, session_id, event_type, actor_id, payload_json, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    event_id,
                    session_id,
                    event_value,
                    actor_id,
                    json.dumps(payload or {}),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        return event_id

    def read(self, session_id: str) -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM events WHERE session_id = ? ORDER BY created_at ASC",
                (session_id,),
            ).fetchall()
        return [
            {
                "id": r["id"],
                "session_id": r["session_id"],
                "event_type": r["event_type"],
                "actor_id": r["actor_id"],
                "payload": json.loads(r["payload_json"]),
                "created_at": r["created_at"],
            }
            for r in rows
        ]
