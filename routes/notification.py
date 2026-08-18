from __future__ import annotations

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from forms import NotificationForm
from helpers import role_required
from models import Doctor, Notification, Patient, db

notification_bp = Blueprint("notification", __name__, url_prefix="/notifications")


@notification_bp.route("/")
@login_required
@role_required("Admin", "Doctor", "Nurse", "Patient", "Pharmacist", "LaboratoryStaff")
def list_notifications():
    notifications_query = Notification.query.order_by(Notification.created_at.desc())
    if current_user.role == "Patient" and current_user.patient_profile:
        notifications_query = notifications_query.filter(
            (Notification.patient_id == current_user.patient_profile.id) | (Notification.patient_id.is_(None))
        )
    elif current_user.role == "Doctor" and current_user.doctor_profile:
        notifications_query = notifications_query.filter(
            (Notification.doctor_id == current_user.doctor_profile.id) | (Notification.doctor_id.is_(None))
        )
    notifications = notifications_query.limit(300).all()
    return render_template("notifications/list.html", notifications=notifications)


@notification_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Nurse", "Doctor", "LaboratoryStaff", "Pharmacist")
def create_notification():
    form = NotificationForm()
    patients = Patient.query.order_by(Patient.id.asc()).all()
    doctors = Doctor.query.order_by(Doctor.id.asc()).all()
    form.patient_id.choices = [(0, "All Patients")] + [
        (patient.id, patient.user.full_name if patient.user else f"Patient {patient.id}") for patient in patients
    ]
    form.doctor_id.choices = [(0, "All Doctors")] + [
        (doctor.id, doctor.user.full_name if doctor.user else f"Doctor {doctor.id}") for doctor in doctors
    ]

    if form.validate_on_submit():
        notification = Notification(
            patient_id=form.patient_id.data or None,
            doctor_id=form.doctor_id.data or None,
            notification_type=form.notification_type.data,
            title=form.title.data.strip(),
            message=form.message.data.strip(),
            status="Unread",
            delivery_status=form.delivery_status.data,
        )
        db.session.add(notification)
        db.session.commit()
        flash("Notification generated successfully.", "success")
        return redirect(url_for("notification.list_notifications"))
    return render_template("notifications/form.html", form=form)


@notification_bp.route("/<int:notification_id>/mark-read", methods=["POST"])
@login_required
@role_required("Admin", "Doctor", "Nurse", "Patient", "Pharmacist", "LaboratoryStaff")
def mark_read(notification_id: int):
    notification = db.session.get(Notification, notification_id)
    if notification is None:
        flash("Notification not found.", "danger")
        return redirect(url_for("notification.list_notifications"))
    notification.status = "Read"
    notification.read_at = datetime.utcnow()
    db.session.commit()
    flash("Notification marked as read.", "success")
    return redirect(url_for("notification.list_notifications"))
