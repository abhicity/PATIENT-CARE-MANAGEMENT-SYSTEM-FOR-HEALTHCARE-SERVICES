from __future__ import annotations

from datetime import date, datetime

from . import db


class Consultation(db.Model):
    __tablename__ = "consultations"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False, index=True)
    consultation_date = db.Column(db.Date, nullable=False, default=date.today)
    symptoms = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    treatment_notes = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    patient = db.relationship("Patient", back_populates="consultations")
    doctor = db.relationship("Doctor", back_populates="consultations")

    def __repr__(self) -> str:
        return f"<Consultation {self.id}>"
