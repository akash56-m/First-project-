import hashlib
from datetime import datetime

from flask import request, session

from app import db
from app.models import AuditLog


def write_audit_log(action: str, details: str, include_ip=True):
    latest = AuditLog.query.order_by(AuditLog.id.desc()).first()
    prev_hash = latest.hash if latest else "0" * 64

    username = session.get("username", "system")
    role = session.get("role", "system")
    user_id = session.get("user_id")
    ip = request.remote_addr if include_ip else "0.0.0.0"

    payload = f"{prev_hash}|{username}|{role}|{action}|{details}|{ip}|{datetime.utcnow().isoformat()}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    log = AuditLog(
        user_id=user_id,
        username=username,
        role=role,
        action=action,
        details=details,
        ip_address=ip,
        prev_hash=prev_hash,
        hash=digest,
    )
    db.session.add(log)
    db.session.commit()
