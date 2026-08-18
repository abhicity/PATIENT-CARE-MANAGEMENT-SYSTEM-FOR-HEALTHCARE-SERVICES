from __future__ import annotations

from . import db


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, unique=True)
    specialization = db.Column(db.String(120), nullable=True)
    qualification = db.Column(db.String(120), nullable=True)
    department = db.Column(db.String(120), nullable=True)
    available_time = db.Column(db.String(120), nullable=True)

    user = db.relationship("User", back_populates="doctor_profile")
    appointments = db.relationship(
        "Appointment",
        back_populates="doctor",
        cascade="all, delete-orphan",
    )
    consultations = db.relationship(
        "Consultation",
        back_populates="doctor",
        cascade="all, delete-orphan",
    )
    prescriptions = db.relationship(
        "Prescription",
        back_populates="doctor",
        cascade="all, delete-orphan",
    )
    laboratory_reports = db.relationship(
        "LaboratoryReport",
        back_populates="doctor",
        cascade="all, delete-orphan",
    )
    notifications = db.relationship(
        "Notification",
        back_populates="doctor",
        cascade="all, delete-orphan",
    )
    feedback_entries = db.relationship(
        "Feedback",
        back_populates="doctor",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Doctor {self.id}>"
