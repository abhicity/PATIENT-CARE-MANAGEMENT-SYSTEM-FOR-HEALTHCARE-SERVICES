from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from forms import LoginForm, RegistrationForm
from helpers import create_profile_for_user
from models import LoginActivity, User, db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
ROLE_MAP = {
    "admin": "Admin",
    "doctor": "Doctor",
    "nurse": "Nurse",
    "patient": "Patient",
    "pharmacist": "Pharmacist",
    "laboratorystaff": "LaboratoryStaff",
}


def _render_role_login(form: LoginForm, role_key: str, expected_role: str):
    return render_template("login.html", form=form, role_key=role_key, expected_role=expected_role)


def _handle_role_login(role_key: str, expected_role: str):
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user is None or not check_password_hash(user.password, form.password.data):
            flash("Invalid email or password.", "danger")
            return _render_role_login(form, role_key, expected_role)

        if user.role != expected_role:
            flash(f"This account is not registered as {expected_role}. Please use the correct login.", "danger")
            return _render_role_login(form, role_key, expected_role)

        login_user(user, remember=form.remember_me.data)
        activity = LoginActivity(
            user_id=user.id,
            role=user.role,
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
            user_agent=(request.user_agent.string or "")[:300],
        )
        db.session.add(activity)
        db.session.commit()
        flash("Logged in successfully.", "success")
        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)
        return redirect(url_for("dashboard.home"))

    return _render_role_login(form, role_key, expected_role)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if existing_user:
            flash("An account with this email already exists.", "danger")
            return render_template("register.html", form=form)

        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.lower().strip(),
            phone=form.phone.data.strip(),
            password=generate_password_hash(form.password.data),
            role=form.role.data,
        )
        create_profile_for_user(user)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully. Please log in from your role login.", "success")
        return redirect(url_for("auth.role_login", role=form.role.data.lower()))

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))
    return render_template("login_select.html", role_map=ROLE_MAP)


@auth_bp.route("/login/<role>", methods=["GET", "POST"])
def role_login(role: str):
    role_key = role.lower().strip()
    expected_role = ROLE_MAP.get(role_key)
    if expected_role is None:
        flash("Invalid role login page selected.", "danger")
        return redirect(url_for("auth.login"))

    return _handle_role_login(role_key, expected_role)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))
