from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from forms import PatientFeedbackForm
from helpers import role_required
from models import Doctor, Feedback, Patient, db

feedback_bp = Blueprint("feedback", __name__, url_prefix="/feedback")


def _feedback_query():
    query = Feedback.query.order_by(Feedback.created_at.desc())
    if current_user.role == "Patient" and current_user.patient_profile:
        query = query.filter(Feedback.patient_id == current_user.patient_profile.id)
    elif current_user.role == "Doctor" and current_user.doctor_profile:
        query = query.filter(Feedback.doctor_id == current_user.doctor_profile.id)
    return query


@feedback_bp.route("/")
@login_required
@role_required("Admin", "Doctor", "Nurse", "Patient")
def list_feedback():
    doctor_filter = request.args.get("doctor_id", type=int)
    rating_filter = request.args.get("rating", type=int)

    query = _feedback_query()
    if doctor_filter:
        query = query.filter(Feedback.doctor_id == doctor_filter)
    if rating_filter:
        query = query.filter(Feedback.doctor_rating == rating_filter)

    entries = query.limit(500).all()
    doctors = Doctor.query.order_by(Doctor.id.asc()).all()

    avg_satisfaction = 0.0
    if entries:
        avg_satisfaction = round(sum(item.average_rating for item in entries) / len(entries), 2)

    return render_template(
        "feedback/list.html",
        entries=entries,
        doctors=doctors,
        avg_satisfaction=avg_satisfaction,
        selected_doctor=doctor_filter or 0,
        selected_rating=rating_filter or 0,
    )


@feedback_bp.route("/add", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Nurse", "Patient")
def add_feedback():
    form = PatientFeedbackForm()
    patients = Patient.query.order_by(Patient.id.asc()).all()
    doctors = Doctor.query.order_by(Doctor.id.asc()).all()

    if not patients:
        flash("Please create patient records before submitting feedback.", "warning")
        return redirect(url_for("feedback.list_feedback"))

    form.patient_id.choices = [(patient.id, patient.user.full_name if patient.user else f"Patient {patient.id}") for patient in patients]
    form.doctor_id.choices = [(0, "Not Applicable")] + [
        (doctor.id, doctor.user.full_name if doctor.user else f"Doctor {doctor.id}") for doctor in doctors
    ]

    if current_user.role == "Patient" and current_user.patient_profile:
        form.patient_id.data = current_user.patient_profile.id

    if form.validate_on_submit():
        doctor = db.session.get(Doctor, form.doctor_id.data) if form.doctor_id.data else None
        department = doctor.department if doctor else None

        entry = Feedback(
            patient_id=form.patient_id.data,
            doctor_id=form.doctor_id.data or None,
            department=department,
            consultation_rating=form.consultation_rating.data,
            doctor_rating=form.doctor_rating.data,
            hospital_service_rating=form.hospital_service_rating.data,
            laboratory_service_rating=form.laboratory_service_rating.data,
            pharmacy_service_rating=form.pharmacy_service_rating.data,
            comments=form.comments.data.strip() if form.comments.data else None,
        )
        db.session.add(entry)
        db.session.commit()
        flash("Feedback submitted successfully.", "success")
        return redirect(url_for("feedback.list_feedback"))

    return render_template("feedback/form.html", form=form, title="Submit Patient Feedback")
