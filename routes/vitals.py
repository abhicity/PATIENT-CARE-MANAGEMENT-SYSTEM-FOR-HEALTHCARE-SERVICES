from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from forms import VitalsForm
from helpers import role_required
from models import Patient, User, Vitals, db

vitals_bp = Blueprint("vitals", __name__, url_prefix="/vitals")


def _choices():
    patients = Patient.query.order_by(Patient.id.asc()).all()
    nurses = User.query.filter_by(role="Nurse").order_by(User.id.asc()).all()
    patient_choices = [(patient.id, patient.user.full_name if patient.user else f"Patient {patient.id}") for patient in patients]
    nurse_choices = [(nurse.id, nurse.full_name) for nurse in nurses]
    return patients, nurses, patient_choices, nurse_choices


@vitals_bp.route("/")
@login_required
@role_required("Admin", "Doctor", "Nurse")
def list_vitals():
    vitals = Vitals.query.order_by(Vitals.recorded_at.desc()).all()
    return render_template("vitals/list.html", vitals=vitals)


@vitals_bp.route("/add", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Doctor", "Nurse")
def add_vitals():
    form = VitalsForm()
    patients, nurses, patient_choices, nurse_choices = _choices()

    if not patients:
        flash("Please create patient records before adding vitals.", "warning")
        return redirect(url_for("vitals.list_vitals"))
    if not nurses:
        flash("Please create a nurse account before adding vitals.", "warning")
        return redirect(url_for("vitals.list_vitals"))

    form.patient_id.choices = patient_choices
    form.recorded_by_id.choices = nurse_choices
    if current_user.role == "Nurse":
        form.recorded_by_id.data = current_user.id

    if form.validate_on_submit():
        vitals_entry = Vitals(
            patient_id=form.patient_id.data,
            recorded_by_id=form.recorded_by_id.data,
            blood_pressure_systolic=form.blood_pressure_systolic.data,
            blood_pressure_diastolic=form.blood_pressure_diastolic.data,
            pulse_rate=form.pulse_rate.data,
            temperature_c=form.temperature_c.data,
            respiratory_rate=form.respiratory_rate.data,
            oxygen_saturation=form.oxygen_saturation.data,
            notes=form.notes.data.strip() if form.notes.data else None,
        )
        db.session.add(vitals_entry)
        db.session.commit()
        flash("Vitals recorded successfully.", "success")
        return redirect(url_for("vitals.list_vitals"))

    return render_template("vitals/form.html", form=form, title="Record Vitals")


@vitals_bp.route("/<int:vitals_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Doctor", "Nurse")
def edit_vitals(vitals_id: int):
    vitals_entry = db.session.get(Vitals, vitals_id)
    if vitals_entry is None:
        flash("Vitals record not found.", "danger")
        return redirect(url_for("vitals.list_vitals"))

    form = VitalsForm(obj=vitals_entry)
    patients, nurses, patient_choices, nurse_choices = _choices()
    form.patient_id.choices = patient_choices
    form.recorded_by_id.choices = nurse_choices
    form.patient_id.data = vitals_entry.patient_id
    form.recorded_by_id.data = vitals_entry.recorded_by_id

    if form.validate_on_submit():
        vitals_entry.patient_id = form.patient_id.data
        vitals_entry.recorded_by_id = form.recorded_by_id.data
        vitals_entry.blood_pressure_systolic = form.blood_pressure_systolic.data
        vitals_entry.blood_pressure_diastolic = form.blood_pressure_diastolic.data
        vitals_entry.pulse_rate = form.pulse_rate.data
        vitals_entry.temperature_c = form.temperature_c.data
        vitals_entry.respiratory_rate = form.respiratory_rate.data
        vitals_entry.oxygen_saturation = form.oxygen_saturation.data
        vitals_entry.notes = form.notes.data.strip() if form.notes.data else None
        db.session.commit()
        flash("Vitals updated successfully.", "success")
        return redirect(url_for("vitals.list_vitals"))

    return render_template("vitals/form.html", form=form, title="Edit Vitals")


@vitals_bp.route("/<int:vitals_id>/delete", methods=["POST"])
@login_required
@role_required("Admin", "Doctor", "Nurse")
def delete_vitals(vitals_id: int):
    vitals_entry = db.session.get(Vitals, vitals_id)
    if vitals_entry is None:
        flash("Vitals record not found.", "danger")
        return redirect(url_for("vitals.list_vitals"))

    db.session.delete(vitals_entry)
    db.session.commit()
    flash("Vitals deleted successfully.", "success")
    return redirect(url_for("vitals.list_vitals"))
