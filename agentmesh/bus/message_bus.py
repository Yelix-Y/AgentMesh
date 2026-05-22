import json
import uuid
from datetime import datetime, timezone

from agentmesh.db.database import get_connection
from agentmesh.models.message import ACPMessage, MessageType


class MessageBus:
    def publish(self, message: ACPMessage) -> None:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO messages
                    (id, thread_id, sender_id, recipient_id, message_type, body, metadata_json, created_at, read)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    message.id,
                    message.thread_id,
                    message.sender_id,
                    message.recipient_id,
                    message.message_type.value,
                    message.body,
                    json.dumps(message.metadata),
                    message.created_at.isoformat(),
                ),
            )

    def poll(self, agent_id: str) -> list[ACPMessage]:
        """Return all unread messages for an agent, oldest first."""
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM messages
                WHERE recipient_id = ? AND read = 0
                ORDER BY created_at ASC
                """,
                (agent_id,),
            ).fetchall()
        return [self._row_to_message(row) for row in rows]

    def consume(self, message_id: str) -> None:
        """Mark a message as read."""
        with get_connection() as conn:
            conn.execute(
                "UPDATE messages SET read = 1 WHERE id = ?",
                (message_id,),
            )

    def get_thread(self, thread_id: str) -> list[ACPMessage]:
        """Return all messages in a thread in chronological order."""
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM messages WHERE thread_id = ? ORDER BY created_at ASC",
                (thread_id,),
            ).fetchall()
        return [self._row_to_message(row) for row in rows]

    def _row_to_message(self, row: object) -> ACPMessage:
        return ACPMessage(
            id=row["id"],
            thread_id=row["thread_id"],
            sender_id=row["sender_id"],
            recipient_id=row["recipient_id"],
            message_type=MessageType(row["message_type"]),
            body=row["body"],
            metadata=json.loads(row["metadata_json"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            read=bool(row["read"]),
        )
