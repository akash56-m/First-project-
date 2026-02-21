from collections import Counter, defaultdict
from datetime import datetime

from flask import Blueprint, jsonify, render_template

from app.models import Complaint

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html", metrics=_dashboard_metrics())


@main_bp.route("/dashboard")
def public_dashboard():
    return render_template("public_dashboard.html", metrics=_dashboard_metrics())


@main_bp.route("/dashboard/data")
def dashboard_data():
    metrics = _dashboard_metrics()
    complaints = Complaint.query.all()

    monthly_counts = defaultdict(int)
    for complaint in complaints:
        monthly_counts[complaint.submitted_at.strftime("%Y-%m")] += 1

    dept_counter = Counter(c.department.name for c in complaints if c.department)
    status_counter = Counter(c.status for c in complaints)

    return jsonify(
        {
            "metrics": metrics,
            "monthly": [{"month": k, "count": v} for k, v in sorted(monthly_counts.items())],
            "departments": [{"name": k, "count": v} for k, v in dept_counter.items()],
            "statuses": [{"status": k, "count": v} for k, v in status_counter.items()],
        }
    )


def _dashboard_metrics():
    complaints = Complaint.query.all()
    total = len(complaints)
    pending = len([c for c in complaints if c.status in {"Pending", "Under Review"}])
    resolved_items = [c for c in complaints if c.status == "Closed" and c.resolved_at]
    resolved = len(resolved_items)

    if resolved_items:
        avg_days = round(
            sum((c.resolved_at - c.submitted_at).total_seconds() / 86400 for c in resolved_items) / resolved,
            2,
        )
    else:
        avg_days = 0

    return {"total": total, "pending": pending, "resolved": resolved, "avg_days": avg_days, "year": datetime.utcnow().year}
