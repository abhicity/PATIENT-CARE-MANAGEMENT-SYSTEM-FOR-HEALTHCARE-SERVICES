from __future__ import annotations

from datetime import datetime

from . import db


class EHRRecord(db.Model):
    __tablename__ = "ehr_records"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, unique=True)
    diagnosis_details = db.Column(db.Text, nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    medications = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = db.relationship("Patient", back_populates="ehr_record")

    def __repr__(self) -> str:
        return f"<EHRRecord {self.id}>"
