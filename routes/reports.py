from __future__ import annotations

import csv
import io
from datetime import datetime

from flask import Blueprint, Response, flash, render_template, request
from flask_login import current_user, login_required

from forms import PatientHistorySearchForm
from helpers import role_required
from models import (
    Appointment,
    Billing,
    Consultation,
    Doctor,
    EHRRecord,
    Feedback,
    LaboratoryReport,
    Patient,
    Prescription,
    User,
)

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _simple_pdf_bytes(title: str, lines: list[str]) -> bytes:
    commands = ["BT", "/F1 14 Tf", "50 800 Td", f"({_escape_pdf_text(title)}) Tj", "ET"]
    y = 780
    for line in lines:
        commands.extend(["BT", "/F1 10 Tf", f"50 {y} Td", f"({_escape_pdf_text(str(line))}) Tj", "ET"])
        y -= 14
        if y < 50:
            break

    stream = "\n".join(commands).encode("latin-1", errors="replace")

    obj1 = b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n"
    obj2 = b"2 0 obj<< /Type /Pages /Count 1 /Kids [3 0 R] >>endobj\n"
    obj3 = b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n"
    obj4 = f"4 0 obj<< /Length {len(stream)} >>stream\n".encode("latin-1") + stream + b"\nendstream endobj\n"
    obj5 = b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n"

    objects = [obj1, obj2, obj3, obj4, obj5]
    pdf = b"%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf += obj

    xref_start = len(pdf)
    pdf += f"xref\n0 {len(offsets)}\n".encode("latin-1")
    pdf += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf += f"{offset:010d} 00000 n \n".encode("latin-1")

    pdf += f"trailer<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode("latin-1")
    return pdf


def _resolve_patient(patient_query: str | None):
    if current_user.role == "Patient":
        return current_user.patient_profile

    if not patient_query:
        return None

    trimmed = patient_query.strip()
    if not trimmed:
        return None

    if trimmed.isdigit():
        if len(trimmed) == 12:
            by_aadhaar = Patient.query.filter_by(aadhaar_number=trimmed).first()
            if by_aadhaar is not None:
                return by_aadhaar
        return Patient.query.get(int(trimmed))

    return (
        Patient.query.join(User, Patient.user_id == User.id)
        .filter(
            (User.full_name.ilike(f"%{trimmed}%"))
            | (User.email.ilike(f"%{trimmed}%"))
            | (User.phone.ilike(f"%{trimmed}%"))
            | (Patient.aadhaar_number.ilike(f"%{trimmed}%"))
        )
        .first()
    )


def _build_timeline(patient: Patient):
    timeline = []
    for consultation in Consultation.query.filter_by(patient_id=patient.id).all():
        timeline.append({"type": "Consultation", "date": consultation.consultation_date, "summary": consultation.diagnosis})
    for prescription in Prescription.query.filter_by(patient_id=patient.id).all():
        timeline.append({"type": "Prescription", "date": prescription.prescribed_on, "summary": f"{prescription.medicine_name} ({prescription.dosage})"})
    for report in LaboratoryReport.query.filter_by(patient_id=patient.id).all():
        timeline.append({"type": "Laboratory", "date": report.test_date, "summary": report.test_type})
    timeline.sort(key=lambda item: item["date"] or datetime.min.date(), reverse=True)
    return timeline


def _patient_context(patient: Patient | None):
    if patient is None:
        return None
    return {
        "patient": patient,
        "ehr_record": EHRRecord.query.filter_by(patient_id=patient.id).first(),
        "consultations": Consultation.query.filter_by(patient_id=patient.id).order_by(Consultation.consultation_date.desc()).all(),
        "prescriptions": Prescription.query.filter_by(patient_id=patient.id).order_by(Prescription.prescribed_on.desc()).all(),
        "lab_reports": LaboratoryReport.query.filter_by(patient_id=patient.id).order_by(LaboratoryReport.test_date.desc()).all(),
        "timeline": _build_timeline(patient),
    }


def _admin_report_data(report_type: str):
    if report_type == "patients":
        headers = ["Patient ID", "Name", "Gender", "Blood Group", "Phone"]
        rows = [
            [
                patient.id,
                patient.user.full_name if patient.user else "-",
                patient.gender or "-",
                patient.blood_group or "-",
                patient.user.phone if patient.user else "-",
            ]
            for patient in Patient.query.all()
        ]
        return headers, rows

    if report_type == "appointments":
        headers = ["ID", "Patient", "Doctor", "Date", "Time", "Status"]
        rows = [
            [
                item.id,
                item.patient.user.full_name if item.patient and item.patient.user else item.patient_id,
                item.doctor.user.full_name if item.doctor and item.doctor.user else item.doctor_id,
                item.appointment_date,
                item.appointment_time,
                item.status,
            ]
            for item in Appointment.query.order_by(Appointment.appointment_date.desc()).all()
        ]
        return headers, rows

    if report_type == "consultations":
        headers = ["ID", "Patient", "Doctor", "Date", "Diagnosis"]
        rows = [
            [
                item.id,
                item.patient.user.full_name if item.patient and item.patient.user else item.patient_id,
                item.doctor.user.full_name if item.doctor and item.doctor.user else item.doctor_id,
                item.consultation_date,
                item.diagnosis,
            ]
            for item in Consultation.query.order_by(Consultation.consultation_date.desc()).all()
        ]
        return headers, rows

    if report_type == "prescriptions":
        headers = ["ID", "Patient", "Doctor", "Date", "Medicine", "Dosage"]
        rows = [
            [
                item.id,
                item.patient.user.full_name if item.patient and item.patient.user else item.patient_id,
                item.doctor.user.full_name if item.doctor and item.doctor.user else item.doctor_id,
                item.prescribed_on,
                item.medicine_name,
                item.dosage,
            ]
            for item in Prescription.query.order_by(Prescription.prescribed_on.desc()).all()
        ]
        return headers, rows

    if report_type == "doctor-performance":
        headers = ["Doctor", "Department", "Consultations", "Avg Feedback"]
        rows = []
        for doctor in Doctor.query.all():
            consult_count = Consultation.query.filter_by(doctor_id=doctor.id).count()
            feedback_items = Feedback.query.filter_by(doctor_id=doctor.id).all()
            avg_fb = round(sum(item.average_rating for item in feedback_items) / len(feedback_items), 2) if feedback_items else 0
            rows.append([doctor.user.full_name if doctor.user else f"Doctor {doctor.id}", doctor.department or "-", consult_count, avg_fb])
        return headers, rows

    if report_type == "department-wise":
        headers = ["Department", "Doctors", "Consultations"]
        rows = []
        departments = {}
        for doctor in Doctor.query.all():
            key = doctor.department or "Unassigned"
            departments.setdefault(key, {"doctors": 0, "consultations": 0})
            departments[key]["doctors"] += 1
            departments[key]["consultations"] += Consultation.query.filter_by(doctor_id=doctor.id).count()
        for department, stats in departments.items():
            rows.append([department, stats["doctors"], stats["consultations"]])
        return headers, rows

    if report_type == "monthly":
        headers = ["Month", "Patient Registrations", "Appointments", "Revenue"]
        data = {}
        for patient in Patient.query.all():
            key = patient.user.created_at.strftime("%Y-%m") if patient.user and patient.user.created_at else "Unknown"
            data.setdefault(key, {"patients": 0, "appointments": 0, "revenue": 0.0})
            data[key]["patients"] += 1
        for appt in Appointment.query.all():
            key = appt.created_at.strftime("%Y-%m") if appt.created_at else "Unknown"
            data.setdefault(key, {"patients": 0, "appointments": 0, "revenue": 0.0})
            data[key]["appointments"] += 1
        for bill in Billing.query.all():
            key = bill.created_at.strftime("%Y-%m") if bill.created_at else "Unknown"
            data.setdefault(key, {"patients": 0, "appointments": 0, "revenue": 0.0})
            data[key]["revenue"] += float(bill.total_amount or 0.0)
        rows = [[month, stats["patients"], stats["appointments"], round(stats["revenue"], 2)] for month, stats in sorted(data.items(), reverse=True)]
        return headers, rows

    return ["Info"], [["Invalid report type"]]


def _patient_report_lines(patient: Patient, context: dict) -> list[str]:
    lines = [
        f"Patient ID: {patient.id}",
        f"Patient Name: {patient.user.full_name if patient.user else '-'}",
        f"Patient Email: {patient.user.email if patient.user else '-'}",
        f"Patient Phone: {patient.user.phone if patient.user else '-'}",
        f"Patient Aadhaar: {patient.aadhaar_number or '-'}",
        f"Age: {patient.age or '-'}",
        f"Gender: {patient.gender or '-'}",
        f"Blood Group: {patient.blood_group or '-'}",
        "",
        f"EHR Diagnosis: {context['ehr_record'].diagnosis_details if context['ehr_record'] else '-'}",
        f"EHR Allergies: {context['ehr_record'].allergies if context['ehr_record'] else '-'}",
        f"EHR Medications: {context['ehr_record'].medications if context['ehr_record'] else '-'}",
        "",
        "Consultations:",
    ]
    for consultation in context["consultations"]:
        lines.append(
            f"- {consultation.consultation_date}: {consultation.diagnosis} | Doctor: "
            f"{consultation.doctor.user.full_name if consultation.doctor and consultation.doctor.user else consultation.doctor_id}"
        )
    lines.append("")
    lines.append("Prescriptions:")
    for prescription in context["prescriptions"]:
        lines.append(f"- {prescription.prescribed_on}: {prescription.medicine_name}, {prescription.dosage}, {prescription.frequency}, {prescription.duration}")
    lines.append("")
    lines.append("Laboratory Reports:")
    for report in context["lab_reports"]:
        lines.append(f"- {report.test_date}: {report.test_type} | Result: {report.result}")
    return lines


@reports_bp.route("/", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Doctor", "Nurse", "Patient")
def search_reports():
    form = PatientHistorySearchForm()
    patient = None

    if current_user.role == "Patient" and current_user.patient_profile:
        patient = current_user.patient_profile
    elif form.validate_on_submit():
        patient = _resolve_patient(form.patient_query.data)
        if patient is None:
            flash("Patient not found for the provided ID or name.", "warning")
    elif request.method == "GET":
        query = request.args.get("q", "").strip()
        if query:
            patient = _resolve_patient(query)
            if patient is None:
                flash("Patient not found for the provided ID or name.", "warning")

    context = _patient_context(patient)
    return render_template("reports/search.html", form=form, context=context)


@reports_bp.route("/history")
@login_required
@role_required("Admin", "Doctor", "Nurse", "Patient")
def medical_history():
    patient = _resolve_patient(request.args.get("q", ""))
    if patient is None and current_user.role != "Patient":
        flash("Search a patient by ID or name to view medical history.", "info")
    context = _patient_context(patient)
    return render_template("reports/history.html", context=context)


@reports_bp.route("/admin-summary")
@login_required
@role_required("Admin", "Doctor", "Nurse")
def admin_summary():
    report_type = request.args.get("type", "patients")
    headers, rows = _admin_report_data(report_type)
    return render_template("reports/admin_summary.html", report_type=report_type, headers=headers, rows=rows)


@reports_bp.route("/export-csv/<string:report_type>")
@login_required
@role_required("Admin", "Doctor", "Nurse")
def export_admin_csv(report_type: str):
    headers, rows = _admin_report_data(report_type)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename={report_type}_report.csv"})


@reports_bp.route("/export-pdf/<string:report_type>")
@login_required
@role_required("Admin", "Doctor", "Nurse")
def export_admin_pdf(report_type: str):
    headers, rows = _admin_report_data(report_type)
    lines = [", ".join(str(h) for h in headers)]
    for row in rows:
        lines.append(" | ".join(str(value) for value in row))
    pdf = _simple_pdf_bytes(f"{report_type.title()} Report", lines)
    return Response(pdf, mimetype="application/pdf", headers={"Content-Disposition": f"attachment; filename={report_type}_report.pdf"})


@reports_bp.route("/download/<int:patient_id>")
@login_required
@role_required("Admin", "Doctor", "Nurse", "Patient")
def download_report(patient_id: int):
    patient = Patient.query.get_or_404(patient_id)
    if current_user.role == "Patient" and current_user.patient_profile and current_user.patient_profile.id != patient_id:
        flash("You can download only your own report.", "danger")
        return render_template("reports/history.html", context=None), 403

    context = _patient_context(patient)
    if context is None:
        return Response("No report found.", mimetype="text/plain")

    lines = _patient_report_lines(patient, context)
    report_text = "\n".join(lines)
    filename = f"patient_{patient.id}_medical_report.txt"
    return Response(report_text, mimetype="text/plain", headers={"Content-Disposition": f"attachment; filename={filename}"})


@reports_bp.route("/download-pdf/<int:patient_id>")
@login_required
@role_required("Admin", "Doctor", "Nurse", "Patient")
def download_report_pdf(patient_id: int):
    patient = Patient.query.get_or_404(patient_id)
    if current_user.role == "Patient" and current_user.patient_profile and current_user.patient_profile.id != patient_id:
        flash("You can download only your own report.", "danger")
        return render_template("reports/history.html", context=None), 403

    context = _patient_context(patient)
    if context is None:
        return Response("No report found.", mimetype="text/plain")

    lines = _patient_report_lines(patient, context)
    pdf = _simple_pdf_bytes("Integrated Patient Care - Medical Report", lines)
    return Response(pdf, mimetype="application/pdf", headers={"Content-Disposition": f"attachment; filename=patient_{patient.id}_medical_report.pdf"})


@reports_bp.route("/download-excel/<int:patient_id>")
@login_required
@role_required("Admin", "Doctor", "Nurse", "Patient")
def download_excel_report(patient_id: int):
    patient = Patient.query.get_or_404(patient_id)
    if current_user.role == "Patient" and current_user.patient_profile and current_user.patient_profile.id != patient_id:
        flash("You can download only your own report.", "danger")
        return render_template("reports/history.html", context=None), 403

    context = _patient_context(patient)
    if context is None:
        return Response("No report found.", mimetype="text/plain")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Section", "Field", "Value"])
    writer.writerow(["Patient", "Patient ID", patient.id])
    writer.writerow(["Patient", "Name", patient.user.full_name if patient.user else "-"])
    writer.writerow(["Patient", "Email", patient.user.email if patient.user else "-"])
    writer.writerow(["Patient", "Phone", patient.user.phone if patient.user else "-"])
    writer.writerow(["Patient", "Aadhaar", patient.aadhaar_number or "-"])
    writer.writerow(["Patient", "Age", patient.age or "-"])
    writer.writerow(["Patient", "Gender", patient.gender or "-"])
    writer.writerow(["Patient", "Blood Group", patient.blood_group or "-"])
    writer.writerow(["EHR", "Diagnosis", context["ehr_record"].diagnosis_details if context["ehr_record"] else "-"])
    writer.writerow(["EHR", "Allergies", context["ehr_record"].allergies if context["ehr_record"] else "-"])
    writer.writerow(["EHR", "Medications", context["ehr_record"].medications if context["ehr_record"] else "-"])
    for consultation in context["consultations"]:
        writer.writerow(["Consultation", consultation.consultation_date, consultation.diagnosis])
    for prescription in context["prescriptions"]:
        writer.writerow(["Prescription", prescription.prescribed_on, f"{prescription.medicine_name} {prescription.dosage} {prescription.frequency} {prescription.duration}"])
    for report in context["lab_reports"]:
        writer.writerow(["Laboratory", report.test_date, f"{report.test_type}: {report.result}"])

    filename = f"patient_{patient.id}_medical_report.csv"
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename={filename}"})
