import uuid
from datetime import datetime, timezone

from agentmesh.db.database import get_connection


class MemoryStore:
    def write(self, agent_id: str, memory_type: str, content: str) -> str:
        assert memory_type in ("short", "long"), f"Invalid memory_type: {memory_type}"
        entry_id = str(uuid.uuid4())
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO agent_memory (id, agent_id, memory_type, content, created_at) VALUES (?, ?, ?, ?, ?)",
                (entry_id, agent_id, memory_type, content, datetime.now(timezone.utc).isoformat()),
            )
        return entry_id

    def read(self, agent_id: str, memory_type: str, requesting_agent_id: str) -> list[dict]:
        if agent_id != requesting_agent_id:
            raise PermissionError(
                f"Agent '{requesting_agent_id}' cannot read memory of agent '{agent_id}'. "
                "Knowledge must travel through the message bus."
            )
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT id, content, created_at FROM agent_memory WHERE agent_id = ? AND memory_type = ? ORDER BY created_at ASC",
                (agent_id, memory_type),
            ).fetchall()
        return [{"id": r["id"], "content": r["content"], "created_at": r["created_at"]} for r in rows]

    def clear_short_term(self, agent_id: str) -> None:
        with get_connection() as conn:
            conn.execute(
                "DELETE FROM agent_memory WHERE agent_id = ? AND memory_type = 'short'",
                (agent_id,),
            )
