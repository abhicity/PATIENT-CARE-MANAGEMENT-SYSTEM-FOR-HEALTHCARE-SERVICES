from __future__ import annotations

import secrets

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash

from forms import DoctorForm
from helpers import role_required
from models import Doctor, User, db

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctors")


def _upsert_doctor_from_form(form: DoctorForm, existing_doctor: Doctor | None = None) -> tuple[bool, str | None]:
    email = form.email.data.lower().strip()
    full_name = form.full_name.data.strip()
    phone = form.phone.data.strip()
    specialization = form.specialization.data or None
    qualification = form.qualification.data.strip() or None
    department = form.department.data or None
    available_time = form.available_time.data.strip() or None

    if existing_doctor is not None:
        user_with_email = User.query.filter_by(email=email).first()
        if existing_doctor.user is not None:
            current_user_id = existing_doctor.user.id
            if user_with_email is not None and user_with_email.id != current_user_id:
                flash("Another account already uses this email.", "danger")
                return False, None
        else:
            if user_with_email is None:
                user_with_email = User(
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    password=generate_password_hash(secrets.token_urlsafe(10)),
                    role="Doctor",
                )
                db.session.add(user_with_email)
                db.session.flush()
            elif user_with_email.role != "Doctor":
                flash("This email is already registered for a non-doctor account.", "danger")
                return False, None
            elif user_with_email.doctor_profile is not None and user_with_email.doctor_profile.id != existing_doctor.id:
                flash("This doctor account is already linked to another doctor profile.", "danger")
                return False, None
            existing_doctor.user = user_with_email

        existing_doctor.user.full_name = full_name
        existing_doctor.user.email = email
        existing_doctor.user.phone = phone
        existing_doctor.specialization = specialization
        existing_doctor.qualification = qualification
        existing_doctor.department = department
        existing_doctor.available_time = available_time
        db.session.commit()
        return True, None

    user = User.query.filter_by(email=email).first()
    temp_password = None
    if user is None:
        temp_password = secrets.token_urlsafe(8)
        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            password=generate_password_hash(temp_password),
            role="Doctor",
        )
        db.session.add(user)
        db.session.flush()
    elif user.role != "Doctor":
        flash("This email is already registered for a non-doctor account.", "danger")
        return False, None

    if user.doctor_profile is None:
        user.doctor_profile = Doctor()

    user.full_name = full_name
    user.phone = phone
    user.doctor_profile.specialization = specialization
    user.doctor_profile.qualification = qualification
    user.doctor_profile.department = department
    user.doctor_profile.available_time = available_time
    db.session.commit()
    return True, temp_password


@doctor_bp.route("/", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Doctor", "Nurse", "Patient")
def list_doctors():
    form = DoctorForm() if current_user.role == "Admin" else None
    if request.method == "POST":
        if current_user.role != "Admin" or form is None:
            abort(403)
        if form.validate_on_submit():
            saved, temp_password = _upsert_doctor_from_form(form)
            if saved:
                flash(
                    "Doctor added successfully."
                    + (f" Temporary password: {temp_password}" if temp_password else ""),
                    "success",
                )
                return redirect(url_for("doctor.list_doctors"))

    query = request.args.get("q", "").strip()
    doctors_query = Doctor.query.join(User, isouter=True)
    if query:
        like_query = f"%{query}%"
        doctors_query = doctors_query.filter(
            (User.full_name.ilike(like_query))
            | (User.email.ilike(like_query))
            | (Doctor.specialization.ilike(like_query))
            | (Doctor.department.ilike(like_query))
        )
    doctors = doctors_query.order_by(Doctor.id.asc()).all()
    return render_template("doctors/list.html", doctors=doctors, query=query, form=form)


@doctor_bp.route("/available")
@login_required
def available_doctors():
    doctors = Doctor.query.order_by(Doctor.id.desc()).all()
    return render_template("doctors/available.html", doctors=doctors)


@doctor_bp.route("/add", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def add_doctor():
    form = DoctorForm()
    if form.validate_on_submit():
        saved, temp_password = _upsert_doctor_from_form(form)
        if saved:
            flash(
                "Doctor added successfully." + (f" Temporary password: {temp_password}" if temp_password else ""),
                "success",
            )
            return redirect(url_for("doctor.list_doctors"))

    return render_template("doctors/form.html", form=form, title="Add Doctor")


@doctor_bp.route("/<int:doctor_id>")
@login_required
@role_required("Admin", "Doctor", "Nurse", "Patient")
def doctor_profile(doctor_id: int):
    doctor = db.session.get(Doctor, doctor_id)
    if doctor is None:
        flash("Doctor not found.", "danger")
        return redirect(url_for("doctor.list_doctors"))
    return render_template("doctors/profile.html", doctor=doctor)


@doctor_bp.route("/<int:doctor_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def edit_doctor(doctor_id: int):
    doctor = db.session.get(Doctor, doctor_id)
    if doctor is None:
        flash("Doctor not found.", "danger")
        return redirect(url_for("doctor.list_doctors"))

    form = DoctorForm(obj=doctor)
    if doctor.user:
        form.full_name.data = doctor.user.full_name
        form.email.data = doctor.user.email
        form.phone.data = doctor.user.phone

    if form.validate_on_submit():
        saved, _temp_password = _upsert_doctor_from_form(form, existing_doctor=doctor)
        if saved:
            flash("Doctor updated successfully.", "success")
            return redirect(url_for("doctor.list_doctors"))

    return render_template("doctors/form.html", form=form, title="Edit Doctor")


@doctor_bp.route("/<int:doctor_id>/delete", methods=["POST"])
@login_required
@role_required("Admin")
def delete_doctor(doctor_id: int):
    doctor = db.session.get(Doctor, doctor_id)
    if doctor is None:
        flash("Doctor not found.", "danger")
        return redirect(url_for("doctor.list_doctors"))
    db.session.delete(doctor)
    db.session.commit()
    flash("Doctor deleted successfully.", "success")
    return redirect(url_for("doctor.list_doctors"))
