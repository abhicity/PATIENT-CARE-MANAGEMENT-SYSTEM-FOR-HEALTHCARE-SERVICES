from __future__ import annotations

import secrets

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash

from forms import PatientForm
from helpers import role_required
from models import Patient, User, db

patient_bp = Blueprint("patient", __name__, url_prefix="/patients")


@patient_bp.route("/")
@login_required
@role_required("Admin", "Doctor", "Nurse")
def list_patients():
    query = request.args.get("q", "").strip()
    patients_query = Patient.query.join(User, isouter=True)
    if query:
        like_query = f"%{query}%"
        patients_query = patients_query.filter(
            (User.full_name.ilike(like_query))
            | (User.email.ilike(like_query))
            | (User.phone.ilike(like_query))
            | (Patient.aadhaar_number.ilike(like_query))
            | (Patient.blood_group.ilike(like_query))
            | (Patient.gender.ilike(like_query))
        )
    patients = patients_query.order_by(Patient.id.desc()).all()
    return render_template("patients/list.html", patients=patients, query=query)


@patient_bp.route("/add", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def add_patient():
    form = PatientForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        aadhaar_number = form.aadhaar_number.data.strip() if form.aadhaar_number.data else None
        if aadhaar_number:
            existing_aadhaar = Patient.query.filter_by(aadhaar_number=aadhaar_number).first()
            if existing_aadhaar and (user is None or existing_aadhaar.user_id != user.id):
                flash("Another patient already uses this Aadhaar number.", "danger")
                return render_template("patients/form.html", form=form, title="Add Patient")
        temp_password = None
        if user is None:
            temp_password = secrets.token_urlsafe(8)
            user = User(
                full_name=form.full_name.data.strip(),
                email=form.email.data.lower().strip(),
                phone=form.phone.data.strip(),
                password=generate_password_hash(temp_password),
                role="Patient",
            )
            db.session.add(user)
            db.session.flush()

        if user.patient_profile is None:
            user.patient_profile = Patient()

        user.full_name = form.full_name.data.strip()
        user.phone = form.phone.data.strip()
        user.patient_profile.age = int(form.age.data) if form.age.data else None
        user.patient_profile.gender = form.gender.data or None
        user.patient_profile.aadhaar_number = aadhaar_number
        user.patient_profile.blood_group = form.blood_group.data.strip() or None
        user.patient_profile.address = form.address.data.strip() or None
        user.patient_profile.medical_history = form.medical_history.data.strip() or None

        db.session.commit()
        flash(
            "Patient added successfully." + (f" Temporary password: {temp_password}" if temp_password else ""),
            "success",
        )
        return redirect(url_for("patient.list_patients"))

    return render_template("patients/form.html", form=form, title="Add Patient")


@patient_bp.route("/<int:patient_id>")
@login_required
@role_required("Admin", "Doctor", "Nurse", "Patient")
def patient_profile(patient_id: int):
    patient = db.session.get(Patient, patient_id)
    if patient is None:
        flash("Patient not found.", "danger")
        return redirect(url_for("patient.list_patients"))
    if current_user.role == "Patient" and current_user.patient_profile and current_user.patient_profile.id != patient_id:
        flash("You can only view your own profile.", "danger")
        return redirect(url_for("dashboard.patient_dashboard"))
    return render_template("patients/profile.html", patient=patient)


@patient_bp.route("/<int:patient_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def edit_patient(patient_id: int):
    patient = db.session.get(Patient, patient_id)
    if patient is None:
        flash("Patient not found.", "danger")
        return redirect(url_for("patient.list_patients"))

    form = PatientForm(obj=patient)
    if patient.user:
        form.full_name.data = patient.user.full_name
        form.email.data = patient.user.email
        form.phone.data = patient.user.phone

    if form.validate_on_submit():
        aadhaar_number = form.aadhaar_number.data.strip() if form.aadhaar_number.data else None
        if aadhaar_number:
            existing_aadhaar = Patient.query.filter_by(aadhaar_number=aadhaar_number).first()
            if existing_aadhaar and existing_aadhaar.id != patient.id:
                flash("Another patient already uses this Aadhaar number.", "danger")
                return render_template("patients/form.html", form=form, title="Edit Patient")
        if patient.user is None:
            user = User(
                full_name=form.full_name.data.strip(),
                email=form.email.data.lower().strip(),
                phone=form.phone.data.strip(),
                password=generate_password_hash(secrets.token_urlsafe(8)),
                role="Patient",
            )
            db.session.add(user)
            db.session.flush()
            patient.user = user
        else:
            patient.user.full_name = form.full_name.data.strip()
            patient.user.email = form.email.data.lower().strip()
            patient.user.phone = form.phone.data.strip()

        patient.age = int(form.age.data) if form.age.data else None
        patient.gender = form.gender.data or None
        patient.aadhaar_number = aadhaar_number
        patient.blood_group = form.blood_group.data.strip() or None
        patient.address = form.address.data.strip() or None
        patient.medical_history = form.medical_history.data.strip() or None
        db.session.commit()
        flash("Patient updated successfully.", "success")
        return redirect(url_for("patient.list_patients"))

    return render_template("patients/form.html", form=form, title="Edit Patient")


@patient_bp.route("/<int:patient_id>/delete", methods=["POST"])
@login_required
@role_required("Admin")
def delete_patient(patient_id: int):
    patient = db.session.get(Patient, patient_id)
    if patient is None:
        flash("Patient not found.", "danger")
        return redirect(url_for("patient.list_patients"))
    db.session.delete(patient)
    db.session.commit()
    flash("Patient deleted successfully.", "success")
    return redirect(url_for("patient.list_patients"))
