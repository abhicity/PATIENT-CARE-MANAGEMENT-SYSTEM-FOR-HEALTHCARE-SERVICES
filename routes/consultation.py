from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from forms import ConsultationForm
from helpers import role_required
from models import Consultation, Doctor, Patient, db

consultation_bp = Blueprint("consultation", __name__, url_prefix="/consultations")


def _base_choices():
    patients = Patient.query.order_by(Patient.id.asc()).all()
    doctors = Doctor.query.order_by(Doctor.id.asc()).all()
    patient_choices = [(patient.id, patient.user.full_name if patient.user else f"Patient {patient.id}") for patient in patients]
    doctor_choices = [(doctor.id, doctor.user.full_name if doctor.user else f"Doctor {doctor.id}") for doctor in doctors]
    return patients, doctors, patient_choices, doctor_choices


def _can_manage_consultation(consultation: Consultation) -> bool:
    if current_user.role == "Admin":
        return True
    if current_user.role == "Doctor" and current_user.doctor_profile:
        return consultation.doctor_id == current_user.doctor_profile.id
    return False


@consultation_bp.route("/")
@login_required
@role_required("Admin", "Doctor", "Nurse", "Patient")
def list_consultations():
    consultations_query = Consultation.query.order_by(Consultation.created_at.desc())
    if current_user.role == "Doctor" and current_user.doctor_profile:
        consultations_query = consultations_query.filter(Consultation.doctor_id == current_user.doctor_profile.id)
    elif current_user.role == "Patient" and current_user.patient_profile:
        consultations_query = consultations_query.filter(Consultation.patient_id == current_user.patient_profile.id)
    consultations = consultations_query.all()
    return render_template("consultations/list.html", consultations=consultations)


@consultation_bp.route("/add", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Doctor")
def add_consultation():
    form = ConsultationForm()
    patients, doctors, patient_choices, doctor_choices = _base_choices()
    if not patients or not doctors:
        flash("Please ensure patient and doctor records exist before adding consultations.", "warning")
        return redirect(url_for("consultation.list_consultations"))

    form.patient_id.choices = patient_choices
    form.doctor_id.choices = doctor_choices
    if current_user.role == "Doctor" and current_user.doctor_profile:
        form.doctor_id.data = current_user.doctor_profile.id

    if form.validate_on_submit():
        consultation = Consultation(
            patient_id=form.patient_id.data,
            doctor_id=current_user.doctor_profile.id if current_user.role == "Doctor" and current_user.doctor_profile else form.doctor_id.data,
            consultation_date=form.consultation_date.data,
            symptoms=form.symptoms.data.strip(),
            diagnosis=form.diagnosis.data.strip(),
            treatment_notes=form.treatment_notes.data.strip(),
        )
        db.session.add(consultation)
        db.session.commit()
        return render_template("consultations/summary.html", consultation=consultation)

    return render_template("consultations/form.html", form=form, title="Consultation Form")


@consultation_bp.route("/<int:consultation_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Doctor")
def edit_consultation(consultation_id: int):
    consultation = db.session.get(Consultation, consultation_id)
    if consultation is None:
        flash("Consultation not found.", "danger")
        return redirect(url_for("consultation.list_consultations"))
    if not _can_manage_consultation(consultation):
        flash("You are not authorized to edit this consultation.", "danger")
        return redirect(url_for("consultation.list_consultations"))

    form = ConsultationForm(obj=consultation)
    patients, doctors, patient_choices, doctor_choices = _base_choices()
    if not patients or not doctors:
        flash("Please ensure patient and doctor records exist before editing consultations.", "warning")
        return redirect(url_for("consultation.list_consultations"))

    form.patient_id.choices = patient_choices
    form.doctor_id.choices = doctor_choices
    form.patient_id.data = consultation.patient_id
    form.doctor_id.data = consultation.doctor_id

    if form.validate_on_submit():
        consultation.patient_id = form.patient_id.data
        consultation.doctor_id = (
            current_user.doctor_profile.id
            if current_user.role == "Doctor" and current_user.doctor_profile
            else form.doctor_id.data
        )
        consultation.consultation_date = form.consultation_date.data
        consultation.symptoms = form.symptoms.data.strip()
        consultation.diagnosis = form.diagnosis.data.strip()
        consultation.treatment_notes = form.treatment_notes.data.strip()
        db.session.commit()
        flash("Consultation updated successfully.", "success")
        return redirect(url_for("consultation.list_consultations"))

    return render_template("consultations/form.html", form=form, title="Edit Consultation")


@consultation_bp.route("/<int:consultation_id>/delete", methods=["POST"])
@login_required
@role_required("Admin", "Doctor")
def delete_consultation(consultation_id: int):
    consultation = db.session.get(Consultation, consultation_id)
    if consultation is None:
        flash("Consultation not found.", "danger")
        return redirect(url_for("consultation.list_consultations"))
    if not _can_manage_consultation(consultation):
        flash("You are not authorized to delete this consultation.", "danger")
        return redirect(url_for("consultation.list_consultations"))

    db.session.delete(consultation)
    db.session.commit()
    flash("Consultation deleted successfully.", "success")
    return redirect(url_for("consultation.list_consultations"))
