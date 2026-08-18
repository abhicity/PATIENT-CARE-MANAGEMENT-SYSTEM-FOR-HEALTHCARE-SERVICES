from __future__ import annotations

from datetime import date

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash

from helpers import role_required
from models import Consultation, Doctor, LaboratoryReport, Patient, Prescription, User, db

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


def _json_error(message: str, status: int):
    return jsonify({"error": message}), status


def _patient_payload(patient: Patient) -> dict:
    return {
        "id": patient.id,
        "user_id": patient.user_id,
        "full_name": patient.user.full_name if patient.user else None,
        "email": patient.user.email if patient.user else None,
        "phone": patient.user.phone if patient.user else None,
        "age": patient.age,
        "gender": patient.gender,
        "blood_group": patient.blood_group,
        "address": patient.address,
        "medical_history": patient.medical_history,
    }


def _doctor_payload(doctor: Doctor) -> dict:
    return {
        "id": doctor.id,
        "user_id": doctor.user_id,
        "full_name": doctor.user.full_name if doctor.user else None,
        "email": doctor.user.email if doctor.user else None,
        "phone": doctor.user.phone if doctor.user else None,
        "specialization": doctor.specialization,
        "qualification": doctor.qualification,
        "department": doctor.department,
        "available_time": doctor.available_time,
    }


def _consultation_payload(consultation: Consultation) -> dict:
    return {
        "id": consultation.id,
        "patient_id": consultation.patient_id,
        "doctor_id": consultation.doctor_id,
        "consultation_date": consultation.consultation_date.isoformat(),
        "symptoms": consultation.symptoms,
        "diagnosis": consultation.diagnosis,
        "treatment_notes": consultation.treatment_notes,
    }


def _prescription_payload(prescription: Prescription) -> dict:
    return {
        "id": prescription.id,
        "patient_id": prescription.patient_id,
        "doctor_id": prescription.doctor_id,
        "prescribed_on": prescription.prescribed_on.isoformat(),
        "medicine_name": prescription.medicine_name,
        "dosage": prescription.dosage,
        "frequency": prescription.frequency,
        "duration": prescription.duration,
        "special_instructions": prescription.special_instructions,
    }


def _lab_payload(report: LaboratoryReport) -> dict:
    return {
        "id": report.id,
        "patient_id": report.patient_id,
        "doctor_id": report.doctor_id,
        "test_type": report.test_type,
        "test_date": report.test_date.isoformat(),
        "result": report.result,
        "remarks": report.remarks,
    }


def _require_json() -> dict | None:
    payload = request.get_json(silent=True)
    if payload is None:
        return None
    return payload


def _parse_iso_date(value: str):
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


@api_bp.get("/patients")
@login_required
def patients_list():
    patients = Patient.query.order_by(Patient.id.asc()).all()
    if current_user.role == "Patient" and current_user.patient_profile:
        patients = [current_user.patient_profile]
    return jsonify([_patient_payload(item) for item in patients])


@api_bp.post("/patients")
@login_required
@role_required("Admin", "Nurse")
def patients_create():
    payload = _require_json()
    if payload is None:
        return _json_error("JSON payload required.", 400)
    full_name = str(payload.get("full_name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    phone = str(payload.get("phone", "")).strip()
    if not full_name or not email or not phone:
        return _json_error("full_name, email and phone are required.", 400)
    existing_user = User.query.filter_by(email=email).first()
    if existing_user is not None:
        return _json_error("User already exists with this email.", 409)

    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        password=generate_password_hash("Patient@12345"),
        role="Patient",
    )
    patient = Patient(
        user=user,
        age=payload.get("age"),
        gender=payload.get("gender"),
        blood_group=payload.get("blood_group"),
        address=payload.get("address"),
        medical_history=payload.get("medical_history"),
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify(_patient_payload(patient)), 201


@api_bp.put("/patients/<int:patient_id>")
@login_required
@role_required("Admin", "Nurse")
def patients_update(patient_id: int):
    patient = db.session.get(Patient, patient_id)
    if patient is None:
        return _json_error("Patient not found.", 404)
    payload = _require_json()
    if payload is None:
        return _json_error("JSON payload required.", 400)
    patient.age = payload.get("age", patient.age)
    patient.gender = payload.get("gender", patient.gender)
    patient.blood_group = payload.get("blood_group", patient.blood_group)
    patient.address = payload.get("address", patient.address)
    patient.medical_history = payload.get("medical_history", patient.medical_history)
    db.session.commit()
    return jsonify(_patient_payload(patient))


@api_bp.delete("/patients/<int:patient_id>")
@login_required
@role_required("Admin")
def patients_delete(patient_id: int):
    patient = db.session.get(Patient, patient_id)
    if patient is None:
        return _json_error("Patient not found.", 404)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({"message": "Patient deleted."})


@api_bp.get("/doctors")
@login_required
def doctors_list():
    doctors = Doctor.query.order_by(Doctor.id.asc()).all()
    return jsonify([_doctor_payload(item) for item in doctors])


@api_bp.get("/consultations")
@login_required
def consultations_list():
    consultations_query = Consultation.query.order_by(Consultation.consultation_date.desc())
    if current_user.role == "Doctor" and current_user.doctor_profile:
        consultations_query = consultations_query.filter_by(doctor_id=current_user.doctor_profile.id)
    elif current_user.role == "Patient" and current_user.patient_profile:
        consultations_query = consultations_query.filter_by(patient_id=current_user.patient_profile.id)
    consultations = consultations_query.all()
    return jsonify([_consultation_payload(item) for item in consultations])


@api_bp.post("/consultations")
@login_required
@role_required("Admin", "Doctor")
def consultations_create():
    payload = _require_json()
    if payload is None:
        return _json_error("JSON payload required.", 400)
    required = ("patient_id", "doctor_id", "consultation_date", "symptoms", "diagnosis", "treatment_notes")
    if any(payload.get(field) in (None, "") for field in required):
        return _json_error("Missing required fields for consultation.", 400)
    parsed_date = _parse_iso_date(str(payload["consultation_date"]))
    if parsed_date is None:
        return _json_error("consultation_date must be YYYY-MM-DD.", 400)
    consultation = Consultation(
        patient_id=int(payload["patient_id"]),
        doctor_id=int(payload["doctor_id"]),
        consultation_date=parsed_date,
        symptoms=str(payload["symptoms"]),
        diagnosis=str(payload["diagnosis"]),
        treatment_notes=str(payload["treatment_notes"]),
    )
    db.session.add(consultation)
    db.session.commit()
    return jsonify(_consultation_payload(consultation)), 201


@api_bp.get("/prescriptions")
@login_required
def prescriptions_list():
    prescriptions_query = Prescription.query.order_by(Prescription.prescribed_on.desc())
    if current_user.role == "Doctor" and current_user.doctor_profile:
        prescriptions_query = prescriptions_query.filter_by(doctor_id=current_user.doctor_profile.id)
    elif current_user.role == "Patient" and current_user.patient_profile:
        prescriptions_query = prescriptions_query.filter_by(patient_id=current_user.patient_profile.id)
    prescriptions = prescriptions_query.all()
    return jsonify([_prescription_payload(item) for item in prescriptions])


@api_bp.post("/prescriptions")
@login_required
@role_required("Admin", "Doctor")
def prescriptions_create():
    payload = _require_json()
    if payload is None:
        return _json_error("JSON payload required.", 400)
    required = ("patient_id", "doctor_id", "prescribed_on", "medicine_name", "dosage", "frequency", "duration")
    if any(payload.get(field) in (None, "") for field in required):
        return _json_error("Missing required fields for prescription.", 400)
    prescribed_on = _parse_iso_date(str(payload["prescribed_on"]))
    if prescribed_on is None:
        return _json_error("prescribed_on must be YYYY-MM-DD.", 400)
    prescription = Prescription(
        patient_id=int(payload["patient_id"]),
        doctor_id=int(payload["doctor_id"]),
        prescribed_on=prescribed_on,
        medicine_name=str(payload["medicine_name"]),
        dosage=str(payload["dosage"]),
        frequency=str(payload["frequency"]),
        duration=str(payload["duration"]),
        special_instructions=payload.get("special_instructions"),
    )
    db.session.add(prescription)
    db.session.commit()
    return jsonify(_prescription_payload(prescription)), 201


@api_bp.get("/laboratory")
@login_required
def laboratory_list():
    reports_query = LaboratoryReport.query.order_by(LaboratoryReport.test_date.desc())
    if current_user.role == "Doctor" and current_user.doctor_profile:
        reports_query = reports_query.filter_by(doctor_id=current_user.doctor_profile.id)
    elif current_user.role == "Patient" and current_user.patient_profile:
        reports_query = reports_query.filter_by(patient_id=current_user.patient_profile.id)
    reports = reports_query.all()
    return jsonify([_lab_payload(item) for item in reports])


@api_bp.post("/laboratory")
@login_required
@role_required("Admin", "Doctor", "Nurse", "LaboratoryStaff")
def laboratory_create():
    payload = _require_json()
    if payload is None:
        return _json_error("JSON payload required.", 400)
    required = ("patient_id", "doctor_id", "test_type", "test_date", "result")
    if any(payload.get(field) in (None, "") for field in required):
        return _json_error("Missing required fields for laboratory report.", 400)
    test_date = _parse_iso_date(str(payload["test_date"]))
    if test_date is None:
        return _json_error("test_date must be YYYY-MM-DD.", 400)
    report = LaboratoryReport(
        patient_id=int(payload["patient_id"]),
        doctor_id=int(payload["doctor_id"]),
        test_type=str(payload["test_type"]),
        test_date=test_date,
        result=str(payload["result"]),
        remarks=payload.get("remarks"),
    )
    db.session.add(report)
    db.session.commit()
    return jsonify(_lab_payload(report)), 201
