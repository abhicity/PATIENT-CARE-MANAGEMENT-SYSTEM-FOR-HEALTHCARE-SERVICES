from __future__ import annotations

from . import db


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, unique=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    blood_group = db.Column(db.String(10), nullable=True)
    aadhaar_number = db.Column(db.String(20), nullable=True, unique=True, index=True)
    address = db.Column(db.Text, nullable=True)
    medical_history = db.Column(db.Text, nullable=True)

    user = db.relationship("User", back_populates="patient_profile")
    appointments = db.relationship(
        "Appointment",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    ehr_record = db.relationship(
        "EHRRecord",
        back_populates="patient",
        uselist=False,
        cascade="all, delete-orphan",
    )
    consultations = db.relationship(
        "Consultation",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    prescriptions = db.relationship(
        "Prescription",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    laboratory_reports = db.relationship(
        "LaboratoryReport",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    billings = db.relationship(
        "Billing",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    notifications = db.relationship(
        "Notification",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    vitals = db.relationship(
        "Vitals",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    feedback_entries = db.relationship(
        "Feedback",
        back_populates="patient",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Patient {self.id}>"
