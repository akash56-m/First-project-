import random
import string

from app.models import Complaint


def generate_tracking_id() -> str:
    while True:
        value = "MIB" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not Complaint.query.filter_by(tracking_id=value).first():
            return value
