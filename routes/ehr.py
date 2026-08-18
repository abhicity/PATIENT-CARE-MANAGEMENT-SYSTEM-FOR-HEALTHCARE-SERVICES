from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from forms import EHRForm
from helpers import role_required
from models import EHRRecord, Patient, User, db

ehr_bp = Blueprint("ehr", __name__, url_prefix="/ehr")


def _patient_choices():
    patients = Patient.query.order_by(Patient.id.asc()).all()
    return patients, [(patient.id, patient.user.full_name if patient.user else f"Patient {patient.id}") for patient in patients]


@ehr_bp.route("/")
@login_required
@role_required("Admin", "Doctor", "Nurse", "Patient")
def list_ehr_records():
    query = request.args.get("q", "").strip()
    records_query = EHRRecord.query.join(Patient, EHRRecord.patient_id == Patient.id).outerjoin(User, Patient.user_id == User.id)

    if current_user.role == "Patient" and current_user.patient_profile:
        records_query = records_query.filter(EHRRecord.patient_id == current_user.patient_profile.id)
    elif query:
        if query.isdigit():
            records_query = records_query.filter(EHRRecord.patient_id == int(query))
        else:
            like_query = f"%{query}%"
            records_query = records_query.filter(User.full_name.ilike(like_query))

    records = records_query.order_by(EHRRecord.updated_at.desc()).all()
    return render_template("ehr/list.html", records=records, query=query)


@ehr_bp.route("/add", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Doctor", "Nurse")
def add_ehr_record():
    form = EHRForm()
    patients, choices = _patient_choices()
    if not patients:
        flash("Please add patients before creating EHR records.", "warning")
        return redirect(url_for("patient.list_patients"))
    form.patient_id.choices = choices

    if form.validate_on_submit():
        record = EHRRecord.query.filter_by(patient_id=form.patient_id.data).first()
        if record is None:
            record = EHRRecord(patient_id=form.patient_id.data)
            db.session.add(record)
        record.diagnosis_details = form.diagnosis_details.data.strip() if form.diagnosis_details.data else None
        record.allergies = form.allergies.data.strip() if form.allergies.data else None
        record.medications = form.medications.data.strip() if form.medications.data else None
        record.notes = form.notes.data.strip() if form.notes.data else None
        db.session.commit()
        flash("EHR record saved successfully.", "success")
        return redirect(url_for("ehr.list_ehr_records"))

    return render_template("ehr/form.html", form=form, title="Create EHR Record")


@ehr_bp.route("/<int:record_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Doctor", "Nurse")
def edit_ehr_record(record_id: int):
    record = db.session.get(EHRRecord, record_id)
    if record is None:
        flash("EHR record not found.", "danger")
        return redirect(url_for("ehr.list_ehr_records"))

    form = EHRForm(obj=record)
    _patients, choices = _patient_choices()
    form.patient_id.choices = choices
    form.patient_id.data = record.patient_id

    if form.validate_on_submit():
        record.patient_id = form.patient_id.data
        record.diagnosis_details = form.diagnosis_details.data.strip() if form.diagnosis_details.data else None
        record.allergies = form.allergies.data.strip() if form.allergies.data else None
        record.medications = form.medications.data.strip() if form.medications.data else None
        record.notes = form.notes.data.strip() if form.notes.data else None
        db.session.commit()
        flash("EHR record updated successfully.", "success")
        return redirect(url_for("ehr.list_ehr_records"))

    return render_template("ehr/form.html", form=form, title="Update EHR Record")


@ehr_bp.route("/<int:record_id>/delete", methods=["POST"])
@login_required
@role_required("Admin", "Doctor", "Nurse")
def delete_ehr_record(record_id: int):
    record = db.session.get(EHRRecord, record_id)
    if record is None:
        flash("EHR record not found.", "danger")
        return redirect(url_for("ehr.list_ehr_records"))

    if current_user.role == "Doctor" and current_user.doctor_profile:
        has_consultation = any(
            consultation.doctor_id == current_user.doctor_profile.id
            for consultation in record.patient.consultations
        )
        if not has_consultation:
            flash("You are not authorized to delete this EHR record.", "danger")
            return redirect(url_for("ehr.list_ehr_records"))

    db.session.delete(record)
    db.session.commit()
    flash("EHR record deleted successfully.", "success")
    return redirect(url_for("ehr.list_ehr_records"))
