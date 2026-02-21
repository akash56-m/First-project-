from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, session, url_for

from app import db
from app.models import Complaint
from app.utils.audit import write_audit_log
from app.utils.forms import UpdateStatusForm
from app.utils.security import role_required

officer_bp = Blueprint("officer", __name__, url_prefix="/officer")
VALID_TRANSITIONS = {
    "Pending": {"Under Review"},
    "Under Review": {"Action Taken"},
    "Action Taken": {"Closed"},
    "Closed": set(),
}


@officer_bp.route("/dashboard")
@role_required("officer")
def dashboard():
    complaints = Complaint.query.filter_by(assigned_to=session["user_id"]).order_by(Complaint.updated_at.desc()).all()
    closed = [c for c in complaints if c.status == "Closed"]
    return render_template("officer/dashboard.html", complaints=complaints, closed_count=len(closed))


@officer_bp.route("/complaints/<int:complaint_id>", methods=["GET", "POST"])
@role_required("officer")
def update_complaint(complaint_id):
    complaint = Complaint.query.filter_by(id=complaint_id, assigned_to=session["user_id"]).first_or_404()
    form = UpdateStatusForm()

    if form.validate_on_submit():
        new_status = form.status.data
        if new_status not in VALID_TRANSITIONS.get(complaint.status, set()):
            flash("Invalid status transition", "danger")
            return redirect(url_for("officer.update_complaint", complaint_id=complaint.id))

        complaint.status = new_status
        complaint.resolution_notes = form.notes.data
        if new_status == "Closed":
            complaint.resolved_at = datetime.utcnow()

        db.session.commit()
        write_audit_log("COMPLAINT_STATUS_UPDATE", f"Complaint {complaint.tracking_id} moved to {new_status}")
        flash("Complaint updated", "success")
        return redirect(url_for("officer.dashboard"))

    return render_template("officer/update_complaint.html", complaint=complaint, form=form)
