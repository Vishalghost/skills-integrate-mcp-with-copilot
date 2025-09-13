"""Audit logging utilities."""
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ..database.config import get_db
from ..database.audit import AuditLog
from ..database.models import User

async def log_event(
    db: AsyncSession,
    action: str,
    entity_type: str,
    actor: Optional[User],
    entity_id: Optional[int] = None,
    details: Optional[str] = None,
    request: Optional[Request] = None
):
    """Log an audit event."""
    log_entry = AuditLog(
        actor_id=actor.id if actor else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=request.client.host if request else None
    )
    db.add(log_entry)
    await db.commit()

def audit_log_middleware(action: str, entity_type: str):
    """Decorator for automatic audit logging of API endpoints."""
    def decorator(func):
        async def wrapper(
            *args,
            request: Request,
            db: AsyncSession = Depends(get_db),
            current_user: Optional[User] = None,
            **kwargs
        ):
            # Execute the original function
            result = await func(*args, **kwargs)
            
            # Log the event
            entity_id = result.get("id") if isinstance(result, dict) else None
            details = str(result) if result else None
            
            await log_event(
                db=db,
                action=action,
                entity_type=entity_type,
                actor=current_user,
                entity_id=entity_id,
                details=details,
                request=request
            )
            
            return result
        return wrapper
    return decorator