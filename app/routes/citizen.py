import os

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from app import db
from app.models import Complaint, Department, Service
from app.utils.forms import ComplaintForm, TrackForm
from app.utils.tracking import generate_tracking_id
from app.utils.security import allowed_file

citizen_bp = Blueprint("citizen", __name__)


@citizen_bp.route("/complaints/submit", methods=["GET", "POST"])
def submit_complaint():
    form = ComplaintForm()
    departments = Department.query.order_by(Department.name).all()
    services = Service.query.order_by(Service.name).all()
    form.department_id.choices = [(d.id, d.name) for d in departments]
    form.service_id.choices = [(s.id, s.name) for s in services]

    if form.validate_on_submit():
        evidence_path = None
        file = form.evidence.data

        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Invalid file type. Only jpg, png, and pdf are permitted.", "danger")
                return render_template("citizen/submit.html", form=form)

            filename = secure_filename(file.filename)
            evidence_name = f"{generate_tracking_id()}_{filename}"
            full_path = os.path.join(current_app.config["UPLOAD_FOLDER"], evidence_name)
            file.save(full_path)
            evidence_path = f"uploads/{evidence_name}"

        complaint = Complaint(
            tracking_id=generate_tracking_id(),
            service_id=form.service_id.data,
            department_id=form.department_id.data,
            description=form.description.data,
            evidence_path=evidence_path,
        )
        db.session.add(complaint)
        db.session.commit()

        return render_template("citizen/confirmation.html", tracking_id=complaint.tracking_id)

    return render_template("citizen/submit.html", form=form)


@citizen_bp.route("/services/<int:department_id>")
def services_by_department(department_id):
    services = Service.query.filter_by(department_id=department_id).all()
    return jsonify([{"id": s.id, "name": s.name} for s in services])


@citizen_bp.route("/complaints/track", methods=["GET", "POST"])
def track_complaint():
    form = TrackForm()
    complaint = None
    if form.validate_on_submit():
        complaint = Complaint.query.filter_by(tracking_id=form.tracking_id.data.upper()).first()
        if not complaint:
            flash("Tracking ID not found", "warning")
    return render_template("citizen/track.html", form=form, complaint=complaint)
