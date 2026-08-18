from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from forms import LaboratoryReportForm
from helpers import role_required
from models import Doctor, LaboratoryReport, Patient, db

laboratory_bp = Blueprint("laboratory", __name__, url_prefix="/laboratory")


def _choices():
    patients = Patient.query.order_by(Patient.id.asc()).all()
    doctors = Doctor.query.order_by(Doctor.id.asc()).all()
    patient_choices = [(patient.id, patient.user.full_name if patient.user else f"Patient {patient.id}") for patient in patients]
    doctor_choices = [(doctor.id, doctor.user.full_name if doctor.user else f"Doctor {doctor.id}") for doctor in doctors]
    return patients, doctors, patient_choices, doctor_choices


def _can_manage_report(report: LaboratoryReport) -> bool:
    if current_user.role in {"Admin", "Nurse", "LaboratoryStaff"}:
        return True
    if current_user.role == "Doctor" and current_user.doctor_profile:
        return report.doctor_id == current_user.doctor_profile.id
    return False


@laboratory_bp.route("/")
@login_required
@role_required("Admin", "Doctor", "Nurse", "Patient", "LaboratoryStaff")
def list_reports():
    reports_query = LaboratoryReport.query.order_by(LaboratoryReport.created_at.desc())
    if current_user.role == "Doctor" and current_user.doctor_profile:
        reports_query = reports_query.filter(LaboratoryReport.doctor_id == current_user.doctor_profile.id)
    elif current_user.role == "Patient" and current_user.patient_profile:
        reports_query = reports_query.filter(LaboratoryReport.patient_id == current_user.patient_profile.id)
    reports = reports_query.all()
    return render_template("laboratory/list.html", reports=reports)


@laboratory_bp.route("/add", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Doctor", "Nurse", "LaboratoryStaff")
def add_report():
    form = LaboratoryReportForm()
    patients, doctors, patient_choices, doctor_choices = _choices()
    if not patients or not doctors:
        flash("Please ensure patient and doctor records exist before adding laboratory reports.", "warning")
        return redirect(url_for("laboratory.list_reports"))

    form.patient_id.choices = patient_choices
    form.doctor_id.choices = doctor_choices
    if current_user.role == "Doctor" and current_user.doctor_profile:
        form.doctor_id.data = current_user.doctor_profile.id

    if form.validate_on_submit():
        report = LaboratoryReport(
            patient_id=form.patient_id.data,
            doctor_id=current_user.doctor_profile.id if current_user.role == "Doctor" and current_user.doctor_profile else form.doctor_id.data,
            test_type=form.test_type.data,
            test_date=form.test_date.data,
            result=form.result.data.strip(),
            remarks=form.remarks.data.strip() if form.remarks.data else None,
        )
        db.session.add(report)
        db.session.commit()
        return render_template("laboratory/summary.html", report=report)

    return render_template("laboratory/form.html", form=form, title="Laboratory Test Request Form")


@laboratory_bp.route("/<int:report_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Doctor", "Nurse", "LaboratoryStaff")
def edit_report(report_id: int):
    report = db.session.get(LaboratoryReport, report_id)
    if report is None:
        flash("Laboratory report not found.", "danger")
        return redirect(url_for("laboratory.list_reports"))
    if not _can_manage_report(report):
        flash("You are not authorized to edit this laboratory report.", "danger")
        return redirect(url_for("laboratory.list_reports"))

    form = LaboratoryReportForm(obj=report)
    patients, doctors, patient_choices, doctor_choices = _choices()
    if not patients or not doctors:
        flash("Please ensure patient and doctor records exist before editing laboratory reports.", "warning")
        return redirect(url_for("laboratory.list_reports"))

    form.patient_id.choices = patient_choices
    form.doctor_id.choices = doctor_choices
    form.patient_id.data = report.patient_id
    form.doctor_id.data = report.doctor_id

    if form.validate_on_submit():
        report.patient_id = form.patient_id.data
        report.doctor_id = (
            current_user.doctor_profile.id
            if current_user.role == "Doctor" and current_user.doctor_profile
            else form.doctor_id.data
        )
        report.test_type = form.test_type.data
        report.test_date = form.test_date.data
        report.result = form.result.data.strip()
        report.remarks = form.remarks.data.strip() if form.remarks.data else None
        db.session.commit()
        flash("Laboratory report updated successfully.", "success")
        return redirect(url_for("laboratory.list_reports"))

    return render_template("laboratory/form.html", form=form, title="Edit Laboratory Report")


@laboratory_bp.route("/<int:report_id>/delete", methods=["POST"])
@login_required
@role_required("Admin", "Doctor", "Nurse", "LaboratoryStaff")
def delete_report(report_id: int):
    report = db.session.get(LaboratoryReport, report_id)
    if report is None:
        flash("Laboratory report not found.", "danger")
        return redirect(url_for("laboratory.list_reports"))
    if not _can_manage_report(report):
        flash("You are not authorized to delete this laboratory report.", "danger")
        return redirect(url_for("laboratory.list_reports"))

    db.session.delete(report)
    db.session.commit()
    flash("Laboratory report deleted successfully.", "success")
    return redirect(url_for("laboratory.list_reports"))
