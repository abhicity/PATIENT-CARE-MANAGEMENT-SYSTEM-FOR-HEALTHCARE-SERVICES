from __future__ import annotations

from datetime import date, datetime

from . import db


class Prescription(db.Model):
    __tablename__ = "prescriptions"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False, index=True)
    prescribed_on = db.Column(db.Date, nullable=False, default=date.today)
    medicine_name = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(120), nullable=False)
    frequency = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.String(120), nullable=False)
    special_instructions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    patient = db.relationship("Patient", back_populates="prescriptions")
    doctor = db.relationship("Doctor", back_populates="prescriptions")

    def __repr__(self) -> str:
        return f"<Prescription {self.id}>"
