from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from forms import AppointmentForm
from helpers import role_required
from models import Appointment, Doctor, Patient, db

appointment_bp = Blueprint("appointment", __name__, url_prefix="/appointments")


@appointment_bp.route("/")
@login_required
def list_appointments():
    if current_user.role == "Admin":
        appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
    elif current_user.role == "Doctor" and current_user.doctor_profile:
        appointments = current_user.doctor_profile.appointments
    elif current_user.role == "Patient" and current_user.patient_profile:
        appointments = current_user.patient_profile.appointments
    else:
        appointments = []
    return render_template("appointments/list.html", appointments=appointments)


@appointment_bp.route("/book", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Patient")
def book_appointment():
    form = AppointmentForm()
    patients = Patient.query.order_by(Patient.id.desc()).all()
    doctors = Doctor.query.order_by(Doctor.id.desc()).all()
    form.patient_id.choices = [(patient.id, patient.user.full_name if patient.user else f"Patient {patient.id}") for patient in patients]
    form.doctor_id.choices = [(doctor.id, doctor.user.full_name if doctor.user else f"Doctor {doctor.id}") for doctor in doctors]

    if current_user.role == "Patient" and current_user.patient_profile:
        form.patient_id.data = current_user.patient_profile.id
        form.patient_id.render_kw = {"readonly": True}

    if form.validate_on_submit():
        if current_user.role == "Patient" and current_user.patient_profile:
            patient_id = current_user.patient_profile.id
        else:
            patient_id = form.patient_id.data

        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=form.doctor_id.data,
            appointment_date=form.appointment_date.data,
            appointment_time=form.appointment_time.data,
            status=form.status.data,
        )
        db.session.add(appointment)
        db.session.commit()
        flash("Appointment booked successfully.", "success")
        return redirect(url_for("appointment.list_appointments"))

    return render_template("appointments/form.html", form=form, title="Book Appointment")


@appointment_bp.route("/<int:appointment_id>/status", methods=["POST"])
@login_required
@role_required("Admin", "Doctor")
def update_status(appointment_id: int):
    appointment = db.session.get(Appointment, appointment_id)
    if appointment is None:
        flash("Appointment not found.", "danger")
        return redirect(url_for("appointment.list_appointments"))

    status = request.form.get("status", "Pending")
    if status in {"Pending", "Confirmed", "Completed", "Cancelled"}:
        appointment.status = status
        db.session.commit()
        flash("Appointment status updated.", "success")
    return redirect(url_for("appointment.list_appointments"))
