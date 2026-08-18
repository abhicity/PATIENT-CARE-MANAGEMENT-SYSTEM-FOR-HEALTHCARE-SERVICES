from __future__ import annotations

from datetime import date, datetime

from . import db


class LaboratoryReport(db.Model):
    __tablename__ = "laboratory_reports"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False, index=True)
    test_type = db.Column(db.String(120), nullable=False)
    test_date = db.Column(db.Date, nullable=False, default=date.today)
    result = db.Column(db.Text, nullable=False)
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    patient = db.relationship("Patient", back_populates="laboratory_reports")
    doctor = db.relationship("Doctor", back_populates="laboratory_reports")

    def __repr__(self) -> str:
        return f"<LaboratoryReport {self.id}>"
