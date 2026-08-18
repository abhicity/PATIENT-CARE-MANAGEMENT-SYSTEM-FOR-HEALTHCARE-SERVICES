from __future__ import annotations

from collections import Counter
from datetime import date

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

from helpers import role_required
from models import (
    Appointment,
    Billing,
    Consultation,
    Doctor,
    Feedback,
    LaboratoryReport,
    LoginActivity,
    Medicine,
    Notification,
    Patient,
    User,
    db,
)

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


def _avg_feedback_score() -> float:
    entries = Feedback.query.all()
    if not entries:
        return 0.0
    return round(sum(item.average_rating for item in entries) / len(entries), 2)


@dashboard_bp.route("/")
@login_required
def home():
    redirect_map = {
        "Admin": "dashboard.admin_dashboard",
        "Doctor": "dashboard.doctor_dashboard",
        "Nurse": "dashboard.nurse_dashboard",
        "Patient": "dashboard.patient_dashboard",
        "Pharmacist": "dashboard.pharmacist_dashboard",
        "LaboratoryStaff": "dashboard.laboratory_staff_dashboard",
    }
    return redirect(url_for(redirect_map.get(current_user.role, "dashboard.patient_dashboard")))


@dashboard_bp.route("/admin")
@login_required
@role_required("Admin")
def admin_dashboard():
    today = date.today()
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()

    nurses = User.query.filter_by(role="Nurse").count()
    pharmacists = User.query.filter_by(role="Pharmacist").count()
    laboratory_staff = User.query.filter_by(role="LaboratoryStaff").count()

    total_medicines = Medicine.query.count()
    low_stock_medicines = Medicine.query.filter(Medicine.stock_quantity <= Medicine.reorder_level).count()

    total_billing = db.session.query(db.func.coalesce(db.func.sum(Billing.total_amount), 0.0)).scalar()
    total_billing = round(float(total_billing or 0.0), 2)

    unread_notifications = Notification.query.filter_by(status="Unread").count()
    recent_logins = LoginActivity.query.order_by(LoginActivity.login_at.desc()).limit(10).all()
    recent_patients = Patient.query.order_by(Patient.id.desc()).limit(5).all()
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all()

    completed_consultations = Consultation.query.count()
    cancelled_appointments = Appointment.query.filter_by(status="Cancelled").count()
    pending_laboratory_reports = LaboratoryReport.query.filter(
        (LaboratoryReport.result.is_(None)) | (LaboratoryReport.result == "")
    ).count()
    total_bills_generated = Billing.query.count()
    avg_satisfaction = _avg_feedback_score()

    monthly_counts = Counter(appt.created_at.strftime("%b") for appt in Appointment.query.all())
    gender_counts = Counter((patient.gender or "Unspecified") for patient in patients)

    doctor_labels = []
    doctor_values = []
    for doctor in doctors:
        doctor_labels.append(doctor.user.full_name if doctor.user else f"Doctor {doctor.id}")
        doctor_values.append(Consultation.query.filter_by(doctor_id=doctor.id).count())

    return render_template(
        "dashboard.html",
        title="Admin Dashboard",
        total_patients=len(patients),
        total_doctors=len(doctors),
        total_nurses=nurses,
        total_pharmacists=pharmacists,
        total_laboratory_staff=laboratory_staff,
        todays_appointments=Appointment.query.filter(Appointment.appointment_date == today).count(),
        total_medicines=total_medicines,
        low_stock_medicines=low_stock_medicines,
        total_billing=total_billing,
        unread_notifications=unread_notifications,
        completed_consultations=completed_consultations,
        cancelled_appointments=cancelled_appointments,
        pending_laboratory_reports=pending_laboratory_reports,
        total_bills_generated=total_bills_generated,
        revenue_summary=total_billing,
        avg_satisfaction=avg_satisfaction,
        recent_logins=recent_logins,
        recent_patients=recent_patients,
        recent_appointments=recent_appointments,
        monthly_labels=list(monthly_counts.keys()),
        monthly_values=list(monthly_counts.values()),
        gender_labels=list(gender_counts.keys()),
        gender_values=list(gender_counts.values()),
        doctor_labels=doctor_labels,
        doctor_values=doctor_values,
    )


@dashboard_bp.route("/doctor")
@login_required
@role_required("Doctor")
def doctor_dashboard():
    doctor = current_user.doctor_profile
    appointments = doctor.appointments if doctor else []
    upcoming = [item for item in appointments if item.appointment_date >= date.today()]
    return render_template(
        "dashboard.html",
        title="Doctor Dashboard",
        total_patients=len({item.patient_id for item in appointments}),
        total_doctors=1,
        total_nurses=0,
        total_pharmacists=0,
        total_laboratory_staff=0,
        todays_appointments=sum(1 for item in appointments if item.appointment_date == date.today()),
        total_medicines=0,
        low_stock_medicines=0,
        total_billing=0,
        unread_notifications=Notification.query.filter(
            (Notification.doctor_id == doctor.id) | (Notification.doctor_id.is_(None))
        ).count()
        if doctor
        else 0,
        completed_consultations=Consultation.query.filter_by(doctor_id=doctor.id).count() if doctor else 0,
        cancelled_appointments=sum(1 for item in appointments if item.status == "Cancelled"),
        pending_laboratory_reports=LaboratoryReport.query.filter_by(doctor_id=doctor.id).count() if doctor else 0,
        total_bills_generated=0,
        revenue_summary=0,
        avg_satisfaction=_avg_feedback_score(),
        recent_logins=[],
        recent_patients=[],
        recent_appointments=appointments[:5],
        monthly_labels=[],
        monthly_values=[],
        gender_labels=[],
        gender_values=[],
        doctor_labels=[],
        doctor_values=[],
        doctor_appointments=appointments,
        upcoming_appointments=upcoming[:5],
    )


@dashboard_bp.route("/nurse")
@login_required
@role_required("Nurse")
def nurse_dashboard():
    return render_template(
        "dashboard.html",
        title="Nurse Dashboard",
        total_patients=Patient.query.count(),
        total_doctors=Doctor.query.count(),
        total_nurses=User.query.filter_by(role="Nurse").count(),
        total_pharmacists=User.query.filter_by(role="Pharmacist").count(),
        total_laboratory_staff=User.query.filter_by(role="LaboratoryStaff").count(),
        todays_appointments=Appointment.query.filter(Appointment.appointment_date == date.today()).count(),
        total_medicines=Medicine.query.count(),
        low_stock_medicines=Medicine.query.filter(Medicine.stock_quantity <= Medicine.reorder_level).count(),
        total_billing=round(float(db.session.query(db.func.coalesce(db.func.sum(Billing.total_amount), 0.0)).scalar() or 0.0), 2),
        unread_notifications=Notification.query.filter_by(status="Unread").count(),
        completed_consultations=Consultation.query.count(),
        cancelled_appointments=Appointment.query.filter_by(status="Cancelled").count(),
        pending_laboratory_reports=LaboratoryReport.query.filter(
            (LaboratoryReport.result.is_(None)) | (LaboratoryReport.result == "")
        ).count(),
        total_bills_generated=Billing.query.count(),
        revenue_summary=round(float(db.session.query(db.func.coalesce(db.func.sum(Billing.total_amount), 0.0)).scalar() or 0.0), 2),
        avg_satisfaction=_avg_feedback_score(),
        recent_logins=LoginActivity.query.order_by(LoginActivity.login_at.desc()).limit(10).all(),
        recent_patients=Patient.query.order_by(Patient.id.desc()).limit(5).all(),
        recent_appointments=Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all(),
        monthly_labels=[],
        monthly_values=[],
        gender_labels=[],
        gender_values=[],
        doctor_labels=[],
        doctor_values=[],
    )


@dashboard_bp.route("/patient")
@login_required
@role_required("Patient")
def patient_dashboard():
    patient = current_user.patient_profile
    appointments = patient.appointments if patient else []
    return render_template(
        "dashboard.html",
        title="Patient Dashboard",
        total_patients=1,
        total_doctors=Doctor.query.count(),
        total_nurses=User.query.filter_by(role="Nurse").count(),
        total_pharmacists=User.query.filter_by(role="Pharmacist").count(),
        total_laboratory_staff=User.query.filter_by(role="LaboratoryStaff").count(),
        todays_appointments=sum(1 for item in appointments if item.appointment_date == date.today()),
        total_medicines=Medicine.query.count(),
        low_stock_medicines=Medicine.query.filter(Medicine.stock_quantity <= Medicine.reorder_level).count(),
        total_billing=round(
            float(
                db.session.query(db.func.coalesce(db.func.sum(Billing.total_amount), 0.0))
                .filter(Billing.patient_id == patient.id)
                .scalar()
                or 0.0
            ),
            2,
        )
        if patient
        else 0,
        unread_notifications=Notification.query.filter(
            (Notification.patient_id == patient.id) | (Notification.patient_id.is_(None))
        ).count()
        if patient
        else 0,
        completed_consultations=Consultation.query.filter_by(patient_id=patient.id).count() if patient else 0,
        cancelled_appointments=sum(1 for item in appointments if item.status == "Cancelled"),
        pending_laboratory_reports=LaboratoryReport.query.filter_by(patient_id=patient.id).count() if patient else 0,
        total_bills_generated=Billing.query.filter_by(patient_id=patient.id).count() if patient else 0,
        revenue_summary=0,
        avg_satisfaction=_avg_feedback_score(),
        recent_logins=[],
        recent_patients=[],
        recent_appointments=appointments[:5],
        monthly_labels=[],
        monthly_values=[],
        gender_labels=[],
        gender_values=[],
        doctor_labels=[],
        doctor_values=[],
        patient_appointments=appointments,
    )


@dashboard_bp.route("/pharmacist")
@login_required
@role_required("Pharmacist")
def pharmacist_dashboard():
    return render_template(
        "dashboard.html",
        title="Pharmacist Dashboard",
        total_patients=Patient.query.count(),
        total_doctors=Doctor.query.count(),
        total_nurses=User.query.filter_by(role="Nurse").count(),
        total_pharmacists=User.query.filter_by(role="Pharmacist").count(),
        total_laboratory_staff=User.query.filter_by(role="LaboratoryStaff").count(),
        todays_appointments=Appointment.query.filter(Appointment.appointment_date == date.today()).count(),
        total_medicines=Medicine.query.count(),
        low_stock_medicines=Medicine.query.filter(Medicine.stock_quantity <= Medicine.reorder_level).count(),
        total_billing=round(float(db.session.query(db.func.coalesce(db.func.sum(Billing.total_amount), 0.0)).scalar() or 0.0), 2),
        unread_notifications=Notification.query.filter_by(status="Unread").count(),
        completed_consultations=Consultation.query.count(),
        cancelled_appointments=Appointment.query.filter_by(status="Cancelled").count(),
        pending_laboratory_reports=LaboratoryReport.query.filter(
            (LaboratoryReport.result.is_(None)) | (LaboratoryReport.result == "")
        ).count(),
        total_bills_generated=Billing.query.count(),
        revenue_summary=round(float(db.session.query(db.func.coalesce(db.func.sum(Billing.total_amount), 0.0)).scalar() or 0.0), 2),
        avg_satisfaction=_avg_feedback_score(),
        recent_logins=[],
        recent_patients=Patient.query.order_by(Patient.id.desc()).limit(5).all(),
        recent_appointments=Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all(),
        monthly_labels=[],
        monthly_values=[],
        gender_labels=[],
        gender_values=[],
        doctor_labels=[],
        doctor_values=[],
    )


@dashboard_bp.route("/laboratory-staff")
@login_required
@role_required("LaboratoryStaff")
def laboratory_staff_dashboard():
    return render_template(
        "dashboard.html",
        title="Laboratory Staff Dashboard",
        total_patients=Patient.query.count(),
        total_doctors=Doctor.query.count(),
        total_nurses=User.query.filter_by(role="Nurse").count(),
        total_pharmacists=User.query.filter_by(role="Pharmacist").count(),
        total_laboratory_staff=User.query.filter_by(role="LaboratoryStaff").count(),
        todays_appointments=Appointment.query.filter(Appointment.appointment_date == date.today()).count(),
        total_medicines=Medicine.query.count(),
        low_stock_medicines=Medicine.query.filter(Medicine.stock_quantity <= Medicine.reorder_level).count(),
        total_billing=round(float(db.session.query(db.func.coalesce(db.func.sum(Billing.total_amount), 0.0)).scalar() or 0.0), 2),
        unread_notifications=Notification.query.filter_by(status="Unread").count(),
        completed_consultations=Consultation.query.count(),
        cancelled_appointments=Appointment.query.filter_by(status="Cancelled").count(),
        pending_laboratory_reports=LaboratoryReport.query.filter(
            (LaboratoryReport.result.is_(None)) | (LaboratoryReport.result == "")
        ).count(),
        total_bills_generated=Billing.query.count(),
        revenue_summary=round(float(db.session.query(db.func.coalesce(db.func.sum(Billing.total_amount), 0.0)).scalar() or 0.0), 2),
        avg_satisfaction=_avg_feedback_score(),
        recent_logins=[],
        recent_patients=Patient.query.order_by(Patient.id.desc()).limit(5).all(),
        recent_appointments=Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all(),
        monthly_labels=[],
        monthly_values=[],
        gender_labels=[],
        gender_values=[],
        doctor_labels=[],
        doctor_values=[],
    )
