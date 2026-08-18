from __future__ import annotations

import os
from datetime import date, timedelta

from flask import Flask, flash, redirect, render_template, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash

from config import Config
from models import (
    Appointment,
    Billing,
    Consultation,
    Doctor,
    EHRRecord,
    Feedback,
    LaboratoryReport,
    Medicine,
    Notification,
    Patient,
    PharmacyDispense,
    Prescription,
    User,
   Vitals,
   db,
)
from helpers import create_profile_for_user, role_required

login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.get(User, int(user_id))


def seed_default_data() -> None:
    admin = User.query.filter_by(email="admin@hospital.local").first()
    if admin is None:
        admin = User(
            full_name="System Admin",
            email="admin@hospital.local",
            phone="9999999999",
            password=generate_password_hash("Admin@12345"),
            role="Admin",
        )
        db.session.add(admin)

    doctor_seed_data = [
        {
            "full_name": "Dr. Alice Morgan",
            "email": "doctor1@hospital.local",
            "phone": "8888888881",
            "specialization": "General Medicine",
            "qualification": "MBBS, MD",
            "department": "Medicine",
            "available_time": "Mon-Fri 09:00-17:00",
        },
        {
            "full_name": "Dr. Brian Carter",
            "email": "doctor2@hospital.local",
            "phone": "8888888882",
            "specialization": "Cardiology",
            "qualification": "MBBS, DM",
            "department": "Cardiology",
            "available_time": "Mon-Sat 10:00-16:00",
        },
        {
            "full_name": "Dr. Clara Bennett",
            "email": "doctor3@hospital.local",
            "phone": "8888888883",
            "specialization": "Pediatrics",
            "qualification": "MBBS, DCH",
            "department": "Pediatrics",
            "available_time": "Tue-Sun 09:00-15:00",
        },
        {
            "full_name": "Dr. Daniel Hughes",
            "email": "doctor4@hospital.local",
            "phone": "8888888884",
            "specialization": "Orthopedics",
            "qualification": "MBBS, MS",
            "department": "Orthopedics",
            "available_time": "Mon-Fri 11:00-18:00",
        },
        {
            "full_name": "Dr. Emily Foster",
            "email": "doctor5@hospital.local",
            "phone": "8888888885",
            "specialization": "Gynecology",
            "qualification": "MBBS, MS",
            "department": "Gynecology",
            "available_time": "Mon-Sat 08:00-14:00",
        },
    ]

    for doctor_data in doctor_seed_data:
        doctor_user = User.query.filter_by(email=doctor_data["email"]).first()
        if doctor_user is None:
            doctor_user = User(
                full_name=doctor_data["full_name"],
                email=doctor_data["email"],
                phone=doctor_data["phone"],
                password=generate_password_hash("Doctor@12345"),
                role="Doctor",
            )
            doctor_user.doctor_profile = Doctor(
                specialization=doctor_data["specialization"],
                qualification=doctor_data["qualification"],
                department=doctor_data["department"],
                available_time=doctor_data["available_time"],
            )
            db.session.add(doctor_user)

    nurse = User.query.filter_by(email="nurse@hospital.local").first()
    if nurse is None:
        nurse = User(
            full_name="Nurse Grace",
            email="nurse@hospital.local",
            phone="7777777777",
            password=generate_password_hash("Nurse@12345"),
            role="Nurse",
        )
        db.session.add(nurse)

    pharmacist = User.query.filter_by(email="pharmacist@hospital.local").first()
    if pharmacist is None:
        pharmacist = User(
            full_name="Pharmacist Mike",
            email="pharmacist@hospital.local",
            phone="7777777701",
            password=generate_password_hash("Pharma@12345"),
            role="Pharmacist",
        )
        db.session.add(pharmacist)

    laboratory_staff = User.query.filter_by(email="labstaff@hospital.local").first()
    if laboratory_staff is None:
        laboratory_staff = User(
            full_name="Lab Staff Rose",
            email="labstaff@hospital.local",
            phone="7777777702",
            password=generate_password_hash("Lab@12345"),
            role="LaboratoryStaff",
        )
        db.session.add(laboratory_staff)

    patient_seed_data = [
        {
            "full_name": "John Patient",
            "email": "patient1@hospital.local",
            "phone": "6666666661",
            "age": 34,
            "gender": "Male",
            "blood_group": "O+",
            "address": "123 Health Street",
            "medical_history": "Seasonal allergies",
        },
        {
            "full_name": "Ava Brown",
            "email": "patient2@hospital.local",
            "phone": "6666666662",
            "age": 28,
            "gender": "Female",
            "blood_group": "A+",
            "address": "45 Green Avenue",
            "medical_history": "Asthma",
        },
        {
            "full_name": "Liam Scott",
            "email": "patient3@hospital.local",
            "phone": "6666666663",
            "age": 41,
            "gender": "Male",
            "blood_group": "B+",
            "address": "78 River Road",
            "medical_history": "Diabetes",
        },
        {
            "full_name": "Sophia Clark",
            "email": "patient4@hospital.local",
            "phone": "6666666664",
            "age": 37,
            "gender": "Female",
            "blood_group": "AB+",
            "address": "90 Lake View",
            "medical_history": "Hypertension",
        },
        {
            "full_name": "Noah Patel",
            "email": "patient5@hospital.local",
            "phone": "6666666665",
            "age": 52,
            "gender": "Male",
            "blood_group": "O-",
            "address": "11 Hill Top",
            "medical_history": "Knee pain",
        },
    ]

    for patient_data in patient_seed_data:
        patient_user = User.query.filter_by(email=patient_data["email"]).first()
        if patient_user is None:
            patient_user = User(
                full_name=patient_data["full_name"],
                email=patient_data["email"],
                phone=patient_data["phone"],
                password=generate_password_hash("Patient@12345"),
                role="Patient",
            )
            patient_user.patient_profile = Patient(
                age=patient_data["age"],
                gender=patient_data["gender"],
                blood_group=patient_data["blood_group"],
                address=patient_data["address"],
                medical_history=patient_data["medical_history"],
            )
            db.session.add(patient_user)

    db.session.commit()


def seed_milestone2_data() -> None:
    patients = Patient.query.order_by(Patient.id.asc()).limit(5).all()
    doctors = Doctor.query.order_by(Doctor.id.asc()).all()
    if not patients or not doctors:
        return

    default_ehr_data = [
        {
            "diagnosis_details": "Seasonal allergies with intermittent sinus congestion.",
            "allergies": "Pollen",
            "medications": "Cetirizine 10mg once daily",
            "notes": "Hydration advised and follow-up in 2 weeks.",
        },
        {
            "diagnosis_details": "Mild asthma under regular monitoring.",
            "allergies": "Dust",
            "medications": "Salbutamol inhaler as needed",
            "notes": "Avoid exposure to dust and smoke.",
        },
        {
            "diagnosis_details": "Type 2 diabetes with stable sugar levels.",
            "allergies": "No known drug allergy",
            "medications": "Metformin 500mg twice daily",
            "notes": "Diet and exercise counseling completed.",
        },
        {
            "diagnosis_details": "Stage-1 hypertension, currently controlled.",
            "allergies": "Penicillin",
            "medications": "Amlodipine 5mg once daily",
            "notes": "Blood pressure log maintained weekly.",
        },
        {
            "diagnosis_details": "Chronic knee pain with reduced mobility.",
            "allergies": "No known allergies",
            "medications": "Paracetamol 650mg as needed",
            "notes": "Physiotherapy recommendation documented.",
        },
    ]

    for index, patient in enumerate(patients):
        doctor = doctors[index % len(doctors)]
        ehr = EHRRecord.query.filter_by(patient_id=patient.id).first()
        if ehr is None:
            data = default_ehr_data[index % len(default_ehr_data)]
            ehr = EHRRecord(patient_id=patient.id, **data)
            db.session.add(ehr)

        consultation_exists = Consultation.query.filter_by(patient_id=patient.id).first()
        if consultation_exists is None:
            consultation = Consultation(
                patient_id=patient.id,
                doctor_id=doctor.id,
                consultation_date=date.today() - timedelta(days=index),
                symptoms=f"Routine symptom checkup #{index + 1}",
                diagnosis=default_ehr_data[index % len(default_ehr_data)]["diagnosis_details"],
                treatment_notes=f"Continue treatment plan #{index + 1} and review after one week.",
            )
            db.session.add(consultation)

        prescription_exists = Prescription.query.filter_by(patient_id=patient.id).first()
        if prescription_exists is None:
            prescription = Prescription(
                patient_id=patient.id,
                doctor_id=doctor.id,
                prescribed_on=date.today() - timedelta(days=index),
                medicine_name=f"Medication {index + 1}",
                dosage="1 tablet",
                frequency="Twice a day",
                duration="7 days",
                special_instructions="Take after food.",
            )
            db.session.add(prescription)

        report_exists = LaboratoryReport.query.filter_by(patient_id=patient.id).first()
        if report_exists is None:
            report = LaboratoryReport(
                patient_id=patient.id,
                doctor_id=doctor.id,
                test_type="Blood Test",
                test_date=date.today() - timedelta(days=index),
                result=f"Lab values within acceptable range for patient {patient.id}.",
                remarks="No critical abnormalities observed.",
            )
            db.session.add(report)

    db.session.commit()


def seed_milestone3_data() -> None:
    patients = Patient.query.order_by(Patient.id.asc()).limit(5).all()
    doctors = Doctor.query.order_by(Doctor.id.asc()).all()
    if not patients:
        return

    medicine_seed_data = [
        {"name": "Paracetamol 650", "category": "Pain Relief", "unit_price": 8.0, "stock_quantity": 180, "reorder_level": 20},
        {"name": "Cetirizine 10", "category": "Allergy", "unit_price": 6.5, "stock_quantity": 140, "reorder_level": 25},
        {"name": "Metformin 500", "category": "Diabetes", "unit_price": 12.0, "stock_quantity": 160, "reorder_level": 30},
        {"name": "Amlodipine 5", "category": "Hypertension", "unit_price": 10.0, "stock_quantity": 120, "reorder_level": 20},
        {"name": "Salbutamol Inhaler", "category": "Respiratory", "unit_price": 140.0, "stock_quantity": 40, "reorder_level": 10},
    ]

    medicines = []
    for medicine_data in medicine_seed_data:
        medicine = Medicine.query.filter_by(name=medicine_data["name"]).first()
        if medicine is None:
            medicine = Medicine(**medicine_data)
            db.session.add(medicine)
        medicines.append(medicine)

    db.session.flush()

    for index, patient in enumerate(patients):
        medicine = medicines[index % len(medicines)]
        doctor = doctors[index % len(doctors)] if doctors else None

        existing_dispense = PharmacyDispense.query.filter_by(patient_id=patient.id, medicine_id=medicine.id).first()
        if existing_dispense is None and medicine.stock_quantity >= 2:
            medicine.stock_quantity -= 2
            db.session.add(
                PharmacyDispense(
                    patient_id=patient.id,
                    medicine_id=medicine.id,
                    quantity=2,
                    notes="Seeded pharmacy dispense for Milestone 3 demo.",
                )
            )

        existing_bill = Billing.query.filter_by(patient_id=patient.id).first()
        if existing_bill is None:
            consultation_charge = float(Consultation.query.filter_by(patient_id=patient.id).count() * 500)
            laboratory_charge = float(LaboratoryReport.query.filter_by(patient_id=patient.id).count() * 350)
            pharmacy_charge = float(medicine.unit_price * 2)
            other_charge = 0.0
            total_amount = consultation_charge + laboratory_charge + pharmacy_charge + other_charge
            db.session.add(
                Billing(
                    invoice_number=f"INV-SEED-{patient.id}",
                    patient_id=patient.id,
                    consultation_charge=consultation_charge,
                    laboratory_charge=laboratory_charge,
                    pharmacy_charge=pharmacy_charge,
                    other_charge=other_charge,
                    total_amount=total_amount,
                    payment_method="UPI",
                    payment_status="Paid",
                    notes="Seeded billing record for Milestone 3.",
                )
            )

        existing_notification = Notification.query.filter_by(patient_id=patient.id, notification_type="Appointment").first()
        if existing_notification is None:
            db.session.add(
                Notification(
                    patient_id=patient.id,
                    doctor_id=doctor.id if doctor else None,
                    title="Appointment Reminder",
                    message=f"Dear {patient.user.full_name if patient.user else f'Patient {patient.id}'}, please attend your follow-up appointment.",
                    notification_type="Appointment",
                    status="Unread",
                    delivery_status="Delivered",
                )
            )

    db.session.commit()


def seed_milestone4_data() -> None:
    patients = Patient.query.order_by(Patient.id.asc()).limit(5).all()
    nurse = User.query.filter_by(role="Nurse").first()
    if not patients or nurse is None:
        return

    vitals_seed_data = [
        {"blood_pressure_systolic": 128, "blood_pressure_diastolic": 84, "pulse_rate": 76, "temperature_c": 37.0, "respiratory_rate": 16, "oxygen_saturation": 98, "notes": "Stable during follow-up visit."},
        {"blood_pressure_systolic": 132, "blood_pressure_diastolic": 88, "pulse_rate": 82, "temperature_c": 37.2, "respiratory_rate": 18, "oxygen_saturation": 97, "notes": "Mildly elevated pressure; advised rest and hydration."},
        {"blood_pressure_systolic": 118, "blood_pressure_diastolic": 78, "pulse_rate": 74, "temperature_c": 36.9, "respiratory_rate": 15, "oxygen_saturation": 99, "notes": "No acute distress observed."},
        {"blood_pressure_systolic": 142, "blood_pressure_diastolic": 90, "pulse_rate": 88, "temperature_c": 37.5, "respiratory_rate": 19, "oxygen_saturation": 96, "notes": "Repeat observation recommended."},
        {"blood_pressure_systolic": 124, "blood_pressure_diastolic": 80, "pulse_rate": 70, "temperature_c": 36.8, "respiratory_rate": 16, "oxygen_saturation": 98, "notes": "Routine vitals documented."},
    ]

    for index, patient in enumerate(patients):
        existing_vitals = Vitals.query.filter_by(patient_id=patient.id).first()
        if existing_vitals is None:
            data = vitals_seed_data[index % len(vitals_seed_data)]
            db.session.add(
                Vitals(
                    patient_id=patient.id,
                    recorded_by_id=nurse.id,
                    blood_pressure_systolic=data["blood_pressure_systolic"],
                    blood_pressure_diastolic=data["blood_pressure_diastolic"],
                    pulse_rate=data["pulse_rate"],
                    temperature_c=data["temperature_c"],
                    respiratory_rate=data["respiratory_rate"],
                    oxygen_saturation=data["oxygen_saturation"],
                    notes=data["notes"],
                )
            )

    db.session.commit()




def seed_milestone4_feedback_data() -> None:
    patients = Patient.query.order_by(Patient.id.asc()).limit(5).all()
    doctors = Doctor.query.order_by(Doctor.id.asc()).all()
    if not patients:
        return

    feedback_seed = [
        {"consultation_rating": 5, "doctor_rating": 5, "hospital_service_rating": 4, "laboratory_service_rating": 4, "pharmacy_service_rating": 5, "comments": "Great consultation and smooth process."},
        {"consultation_rating": 4, "doctor_rating": 4, "hospital_service_rating": 4, "laboratory_service_rating": 3, "pharmacy_service_rating": 4, "comments": "Good support from staff and doctor."},
        {"consultation_rating": 5, "doctor_rating": 5, "hospital_service_rating": 5, "laboratory_service_rating": 4, "pharmacy_service_rating": 4, "comments": "Very satisfied with consultation quality."},
        {"consultation_rating": 4, "doctor_rating": 4, "hospital_service_rating": 5, "laboratory_service_rating": 4, "pharmacy_service_rating": 4, "comments": "Facilities are clean and service is quick."},
        {"consultation_rating": 5, "doctor_rating": 5, "hospital_service_rating": 5, "laboratory_service_rating": 5, "pharmacy_service_rating": 5, "comments": "Excellent overall care experience."},
    ]

    for index, patient in enumerate(patients):
        existing = Feedback.query.filter_by(patient_id=patient.id).first()
        if existing is not None:
            continue
        doctor = doctors[index % len(doctors)] if doctors else None
        data = feedback_seed[index % len(feedback_seed)]
        db.session.add(
            Feedback(
                patient_id=patient.id,
                doctor_id=doctor.id if doctor else None,
                department=doctor.department if doctor else None,
                consultation_rating=data["consultation_rating"],
                doctor_rating=data["doctor_rating"],
                hospital_service_rating=data["hospital_service_rating"],
                laboratory_service_rating=data["laboratory_service_rating"],
                pharmacy_service_rating=data["pharmacy_service_rating"],
                comments=data["comments"],
            )
        )

    db.session.commit()


def ensure_schema_updates() -> None:
    inspector = inspect(db.engine)
    patient_columns = {column["name"] for column in inspector.get_columns("patients")}
    if "aadhaar_number" not in patient_columns:
        db.session.execute(text("ALTER TABLE patients ADD COLUMN aadhaar_number VARCHAR(20)"))
        db.session.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_patients_aadhaar_number ON patients (aadhaar_number)"))
        db.session.commit()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from routes.appointment import appointment_bp
    from routes.api import api_bp
    from routes.auth import auth_bp
    from routes.billing import billing_bp
    from routes.consultation import consultation_bp
    from routes.dashboard import dashboard_bp
    from routes.doctor import doctor_bp
    from routes.ehr import ehr_bp
    from routes.feedback import feedback_bp
    from routes.laboratory import laboratory_bp
    from routes.notification import notification_bp
    from routes.patient import patient_bp
    from routes.pharmacy import pharmacy_bp
    from routes.prescription import prescription_bp
    from routes.reports import reports_bp
    from routes.vitals import vitals_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(ehr_bp)
    app.register_blueprint(consultation_bp)
    app.register_blueprint(prescription_bp)
    app.register_blueprint(laboratory_bp)
    app.register_blueprint(pharmacy_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(vitals_bp)
    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/admin")
    def admin_alias():
        return redirect(url_for("dashboard.admin_dashboard"))

    @app.route("/doctor")
    def doctor_alias():
        return redirect(url_for("dashboard.doctor_dashboard"))

    @app.route("/nurse")
    def nurse_alias():
        return redirect(url_for("dashboard.nurse_dashboard"))

    @app.route("/patient")
    def patient_alias():
        return redirect(url_for("dashboard.patient_dashboard"))

    @app.route("/pharmacist")
    def pharmacist_alias():
        return redirect(url_for("dashboard.pharmacist_dashboard"))

    @app.route("/laboratory-staff")
    def laboratory_staff_alias():
        return redirect(url_for("dashboard.laboratory_staff_dashboard"))

    @app.errorhandler(403)
    def forbidden(_error):
        flash("You do not have permission to access that page.", "danger")
        return redirect(url_for("dashboard.home"))

    with app.app_context():
        os.makedirs(os.path.join(app.root_path, "database"), exist_ok=True)
        db.create_all()
        ensure_schema_updates()
        seed_default_data()
        seed_milestone2_data()
        seed_milestone3_data()
        seed_milestone4_data()
        seed_milestone4_feedback_data()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
