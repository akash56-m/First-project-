from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app import db
from app.models import AuditLog, Complaint, Department, Service, User
from app.utils.audit import write_audit_log
from app.utils.security import hash_password, role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@role_required("admin")
def dashboard():
    complaints = Complaint.query.order_by(Complaint.submitted_at.desc()).all()
    officers = User.query.filter_by(role="officer").all()
    departments = Department.query.order_by(Department.name).all()
    return render_template(
        "admin/dashboard.html",
        complaints=complaints,
        officers=officers,
        departments=departments,
    )


@admin_bp.route("/departments", methods=["POST"])
@role_required("admin")
def create_department():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Department name is required", "danger")
        return redirect(url_for("admin.dashboard"))

    dep = Department(name=name, description=request.form.get("description", "").strip())
    db.session.add(dep)
    db.session.commit()
    write_audit_log("CREATE_DEPARTMENT", f"Department created: {name}")
    flash("Department created", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/services", methods=["POST"])
@role_required("admin")
def create_service():
    name = request.form.get("name", "").strip()
    department_id = request.form.get("department_id")
    if not name or not department_id:
        flash("Service name and department are required", "danger")
        return redirect(url_for("admin.dashboard"))

    service = Service(name=name, department_id=int(department_id), description=request.form.get("description", "").strip())
    db.session.add(service)
    db.session.commit()
    write_audit_log("CREATE_SERVICE", f"Service created: {name}")
    flash("Service created", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/officers", methods=["POST"])
@role_required("admin")
def create_officer():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    department_id = request.form.get("department_id")

    if not username or not password or not department_id:
        flash("Officer details are required", "danger")
        return redirect(url_for("admin.dashboard"))

    officer = User(
        username=username,
        password_hash=hash_password(password),
        role="officer",
        department_id=int(department_id),
    )
    db.session.add(officer)
    db.session.commit()
    write_audit_log("CREATE_OFFICER", f"Officer created: {username}")
    flash("Officer account created", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/assign/<int:complaint_id>", methods=["POST"])
@role_required("admin")
def assign_complaint(complaint_id):
    officer_id = int(request.form["officer_id"])
    complaint = Complaint.query.get_or_404(complaint_id)
    complaint.assigned_to = officer_id
    db.session.commit()
    write_audit_log("ASSIGN_COMPLAINT", f"Complaint {complaint.tracking_id} assigned to officer {officer_id}")
    flash("Complaint assigned", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/audit-logs")
@role_required("admin")
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(500).all()
    return render_template("admin/audit_logs.html", logs=logs)
