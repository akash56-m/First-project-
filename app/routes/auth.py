from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, session, url_for

from app import db
from app.models import User
from app.utils.audit import write_audit_log
from app.utils.forms import LoginForm
from app.utils.security import verify_password

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip(), is_active=True).first()
        if user and verify_password(user.password_hash, form.password.data):
            session.clear()
            session.permanent = True
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            session["department_id"] = user.department_id

            user.last_login = datetime.utcnow()
            db.session.commit()
            write_audit_log("LOGIN", "User logged in")

            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("officer.dashboard"))

        flash("Invalid credentials", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    if session.get("user_id"):
        write_audit_log("LOGOUT", "User logged out")
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("main.index"))
