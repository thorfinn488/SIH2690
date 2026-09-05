from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.audit_repository import AuditRepository


def log_audit_event(db: Session, user_id: Optional[str], action: str, metadata: Optional[Dict[str, Any]] = None):
    """
    Utility function to insert an audit log record into the database.
    """
    try:
        repo = AuditRepository(db)
        return repo.log_action(user_id=user_id, action=action, metadata=metadata)
    except Exception as exc:
        # Prevent audit log failures from interrupting primary transactions
        pass
