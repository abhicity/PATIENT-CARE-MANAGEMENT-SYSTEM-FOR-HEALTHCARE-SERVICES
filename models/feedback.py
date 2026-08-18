from __future__ import annotations

from datetime import datetime

from . import db


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=True, index=True)
    department = db.Column(db.String(120), nullable=True)
    consultation_rating = db.Column(db.Integer, nullable=False, default=5)
    doctor_rating = db.Column(db.Integer, nullable=False, default=5)
    hospital_service_rating = db.Column(db.Integer, nullable=False, default=5)
    laboratory_service_rating = db.Column(db.Integer, nullable=False, default=5)
    pharmacy_service_rating = db.Column(db.Integer, nullable=False, default=5)
    comments = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    patient = db.relationship("Patient", back_populates="feedback_entries")
    doctor = db.relationship("Doctor", back_populates="feedback_entries")

    @property
    def average_rating(self) -> float:
        values = [
            self.consultation_rating,
            self.doctor_rating,
            self.hospital_service_rating,
            self.laboratory_service_rating,
            self.pharmacy_service_rating,
        ]
        return round(sum(values) / len(values), 2)

    def __repr__(self) -> str:
        return f"<Feedback {self.id}>"
