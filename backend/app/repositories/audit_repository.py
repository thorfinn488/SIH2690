from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_action(self, user_id: Optional[str], action: str, metadata: Optional[Dict[str, Any]] = None) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            log_metadata=metadata or {},
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry
