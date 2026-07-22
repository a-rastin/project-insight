from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .db import DatabaseAdapter


def now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def session_row(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "userId": row["user_id"],
        "role": row["role"],
        "authSessionId": row["auth_session_id"],
        "authExpiresAt": row["auth_expires_at"],
        "active": bool(row["active"]),
        "createdAt": row["created_at"],
        "disclaimerAcceptedAt": row["disclaimer_accepted_at"],
    }


class DashboardRepository:
    def __init__(self, adapter: DatabaseAdapter) -> None:
        self.adapter = adapter

    def initialize(self) -> None:
        self.adapter.initialize()

    def ping(self) -> bool:
        return self.adapter.ping()

    def create_session(self, session_id: str, user_id: str, role: str, auth_session_id: str, auth_expires_at: str) -> dict[str, Any]:
        with self.adapter.connect() as conn:
            conn.execute(
                """
                INSERT INTO dashboard_sessions (id, user_id, role, auth_session_id, auth_expires_at, active, created_at)
                VALUES (?, ?, ?, ?, ?, 1, ?)
                """,
                (session_id, user_id, role, auth_session_id, auth_expires_at, now_iso()),
            )
        session = self.get_session(session_id)
        assert session is not None
        return session

    def get_session(self, session_id: str | None) -> dict[str, Any] | None:
        if not session_id:
            return None
        with self.adapter.connect() as conn:
            row = conn.execute("SELECT * FROM dashboard_sessions WHERE id = ?", (session_id,)).fetchone()
        session = session_row(row) if row else None
        return session if session and session["active"] else None

    def update_session_auth(
        self, session_id: str, user_id: str, role: str, auth_session_id: str, auth_expires_at: str
    ) -> None:
        with self.adapter.connect() as conn:
            conn.execute(
                "UPDATE dashboard_sessions SET user_id = ?, role = ?, auth_session_id = ?, auth_expires_at = ? WHERE id = ?",
                (user_id, role, auth_session_id, auth_expires_at, session_id),
            )

    def deactivate_session(self, session_id: str) -> None:
        with self.adapter.connect() as conn:
            conn.execute("UPDATE dashboard_sessions SET active = 0 WHERE id = ?", (session_id,))

    def create_workflow_context(
        self, context_id: str, session_id: str, patient_uuid: str, encounter_uuid: str, expires_at: str
    ) -> None:
        with self.adapter.connect() as conn:
            conn.execute(
                """
                INSERT INTO workflow_contexts (id, dashboard_session_id, patient_uuid, encounter_uuid, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (context_id, session_id, patient_uuid, encounter_uuid, expires_at, now_iso()),
            )

    def get_workflow_context(self, context_id: str | None, session_id: str) -> dict[str, str] | None:
        if not context_id:
            return None
        with self.adapter.connect() as conn:
            row = conn.execute(
                "SELECT * FROM workflow_contexts WHERE id = ? AND dashboard_session_id = ?",
                (context_id, session_id),
            ).fetchone()
        if not row:
            return None
        expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
        if (expires_at if expires_at.tzinfo else expires_at.replace(tzinfo=UTC)) <= datetime.now(UTC):
            return None
        return {"patientUuid": row["patient_uuid"], "encounterUuid": row["encounter_uuid"]}

    def accept_disclaimer(self, session_id: str) -> str:
        accepted_at = now_iso()
        with self.adapter.connect() as conn:
            conn.execute("UPDATE dashboard_sessions SET disclaimer_accepted_at = ? WHERE id = ?", (accepted_at, session_id))
        return accepted_at

    def record_event(self, session: dict[str, Any], event_type: str) -> None:
        with self.adapter.connect() as conn:
            conn.execute(
                """
                INSERT INTO workspace_events (dashboard_session_id, user_id, role, event_type, at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session["id"], session["userId"], session["role"], event_type, now_iso()),
            )
