import os
from functools import wraps
from pathlib import Path

from flask import abort, current_app, session
from werkzeug.security import check_password_hash, generate_password_hash


ALLOWED_ROLES = {"admin", "officer"}


def hash_password(password: str) -> str:
    return generate_password_hash(password, method="pbkdf2:sha256")


def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session or session.get("role") not in roles:
                abort(403)
            return f(*args, **kwargs)

        return wrapped

    return decorator


def allowed_file(filename: str) -> bool:
    extension = Path(filename).suffix.lower()
    return extension in current_app.config["UPLOAD_EXTENSIONS"]


def ensure_upload_dir(path: str):
    os.makedirs(path, exist_ok=True)
