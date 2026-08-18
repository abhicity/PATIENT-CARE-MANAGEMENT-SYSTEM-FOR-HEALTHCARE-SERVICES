from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from forms import PrescriptionForm
from helpers import role_required
from models import Doctor, Patient, Prescription, db

prescription_bp = Blueprint("prescription", __name__, url_prefix="/prescriptions")


def _choices():
    patients = Patient.query.order_by(Patient.id.asc()).all()
    doctors = Doctor.query.order_by(Doctor.id.asc()).all()
    patient_choices = [(patient.id, patient.user.full_name if patient.user else f"Patient {patient.id}") for patient in patients]
    doctor_choices = [(doctor.id, doctor.user.full_name if doctor.user else f"Doctor {doctor.id}") for doctor in doctors]
    return patients, doctors, patient_choices, doctor_choices


def _can_manage_prescription(prescription: Prescription) -> bool:
    if current_user.role == "Admin":
        return True
    if current_user.role == "Doctor" and current_user.doctor_profile:
        return prescription.doctor_id == current_user.doctor_profile.id
    return False


@prescription_bp.route("/")
@login_required
@role_required("Admin", "Doctor", "Nurse", "Patient")
def list_prescriptions():
    prescriptions_query = Prescription.query.order_by(Prescription.created_at.desc())
    if current_user.role == "Doctor" and current_user.doctor_profile:
        prescriptions_query = prescriptions_query.filter(Prescription.doctor_id == current_user.doctor_profile.id)
    elif current_user.role == "Patient" and current_user.patient_profile:
        prescriptions_query = prescriptions_query.filter(Prescription.patient_id == current_user.patient_profile.id)
    prescriptions = prescriptions_query.all()
    return render_template("prescriptions/list.html", prescriptions=prescriptions)


@prescription_bp.route("/add", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Doctor")
def add_prescription():
    form = PrescriptionForm()
    patients, doctors, patient_choices, doctor_choices = _choices()
    if not patients or not doctors:
        flash("Please ensure patient and doctor records exist before adding prescriptions.", "warning")
        return redirect(url_for("prescription.list_prescriptions"))

    form.patient_id.choices = patient_choices
    form.doctor_id.choices = doctor_choices
    if current_user.role == "Doctor" and current_user.doctor_profile:
        form.doctor_id.data = current_user.doctor_profile.id

    if form.validate_on_submit():
        prescription = Prescription(
            patient_id=form.patient_id.data,
            doctor_id=current_user.doctor_profile.id if current_user.role == "Doctor" and current_user.doctor_profile else form.doctor_id.data,
            prescribed_on=form.prescribed_on.data,
            medicine_name=form.medicine_name.data.strip(),
            dosage=form.dosage.data.strip(),
            frequency=form.frequency.data.strip(),
            duration=form.duration.data.strip(),
            special_instructions=form.special_instructions.data.strip() if form.special_instructions.data else None,
        )
        db.session.add(prescription)
        db.session.commit()
        return render_template("prescriptions/summary.html", prescription=prescription)

    return render_template("prescriptions/form.html", form=form, title="Prescription Form")


@prescription_bp.route("/<int:prescription_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Doctor")
def edit_prescription(prescription_id: int):
    prescription = db.session.get(Prescription, prescription_id)
    if prescription is None:
        flash("Prescription not found.", "danger")
        return redirect(url_for("prescription.list_prescriptions"))
    if not _can_manage_prescription(prescription):
        flash("You are not authorized to edit this prescription.", "danger")
        return redirect(url_for("prescription.list_prescriptions"))

    form = PrescriptionForm(obj=prescription)
    patients, doctors, patient_choices, doctor_choices = _choices()
    if not patients or not doctors:
        flash("Please ensure patient and doctor records exist before editing prescriptions.", "warning")
        return redirect(url_for("prescription.list_prescriptions"))

    form.patient_id.choices = patient_choices
    form.doctor_id.choices = doctor_choices
    form.patient_id.data = prescription.patient_id
    form.doctor_id.data = prescription.doctor_id

    if form.validate_on_submit():
        prescription.patient_id = form.patient_id.data
        prescription.doctor_id = (
            current_user.doctor_profile.id
            if current_user.role == "Doctor" and current_user.doctor_profile
            else form.doctor_id.data
        )
        prescription.prescribed_on = form.prescribed_on.data
        prescription.medicine_name = form.medicine_name.data.strip()
        prescription.dosage = form.dosage.data.strip()
        prescription.frequency = form.frequency.data.strip()
        prescription.duration = form.duration.data.strip()
        prescription.special_instructions = (
            form.special_instructions.data.strip() if form.special_instructions.data else None
        )
        db.session.commit()
        flash("Prescription updated successfully.", "success")
        return redirect(url_for("prescription.list_prescriptions"))

    return render_template("prescriptions/form.html", form=form, title="Edit Prescription")


@prescription_bp.route("/<int:prescription_id>/delete", methods=["POST"])
@login_required
@role_required("Admin", "Doctor")
def delete_prescription(prescription_id: int):
    prescription = db.session.get(Prescription, prescription_id)
    if prescription is None:
        flash("Prescription not found.", "danger")
        return redirect(url_for("prescription.list_prescriptions"))
    if not _can_manage_prescription(prescription):
        flash("You are not authorized to delete this prescription.", "danger")
        return redirect(url_for("prescription.list_prescriptions"))

    db.session.delete(prescription)
    db.session.commit()
    flash("Prescription deleted successfully.", "success")
    return redirect(url_for("prescription.list_prescriptions"))
