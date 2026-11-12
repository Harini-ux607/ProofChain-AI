import json
from datetime import datetime
from uuid import uuid4

from app.db.database import get_connection


def create_audit_log(action: str, details: dict) -> dict:
    """Create and permanently save an audit record."""

    audit = {
        "audit_id": f"AUD-{uuid4().hex[:10].upper()}",
        "action": action,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO audit_logs
        (audit_id, action, details, timestamp)
        VALUES (?, ?, ?, ?)
        """,
        (
            audit["audit_id"],
            audit["action"],
            json.dumps(audit["details"]),
            audit["timestamp"]
        )
    )

    connection.commit()
    connection.close()

    return audit


def get_audit_logs() -> list:
    """Retrieve all saved audit records."""

    connection = get_connection()

    rows = connection.execute(
        "SELECT * FROM audit_logs ORDER BY id DESC"
    ).fetchall()

    connection.close()

    logs = []

    for row in rows:
        logs.append({
            "audit_id": row["audit_id"],
            "action": row["action"],
            "details": json.loads(row["details"]),
            "timestamp": row["timestamp"]
        })

    return logs