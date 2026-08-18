from __future__ import annotations

from datetime import datetime

from . import db


class Vitals(db.Model):
    __tablename__ = "vitals"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    recorded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    blood_pressure_systolic = db.Column(db.Integer, nullable=True)
    blood_pressure_diastolic = db.Column(db.Integer, nullable=True)
    pulse_rate = db.Column(db.Integer, nullable=True)
    temperature_c = db.Column(db.Float, nullable=True)
    respiratory_rate = db.Column(db.Integer, nullable=True)
    oxygen_saturation = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    patient = db.relationship("Patient", back_populates="vitals")
    recorded_by_user = db.relationship("User", back_populates="vitals_recorded")

    def __repr__(self) -> str:
        return f"<Vitals {self.id}>"
