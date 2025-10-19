from typing import Any, Dict
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models import AgentRequestRow

class AgentRequestRepository:
    def __init__(self, session_factory=SessionLocal):
        self._sf = session_factory

    def save_success(self, *, query_text: str, response: Dict[str, Any]) -> int:
        with self._sf() as s:
            row = AgentRequestRow(
                query_text=query_text,
                agent_response=response,
                status="success",
            )
            s.add(row)
            s.commit()
            s.refresh(row)
            return row.id

    def save_error(self, *, query_text: str, error_detail: str) -> int:
        with self._sf() as s:
            row = AgentRequestRow(
                query_text=query_text,
                agent_response=None,
                status="error",
                error_detail=error_detail,
            )
            s.add(row)
            s.commit()
            s.refresh(row)
            return row.id