from __future__ import annotations

from datetime import datetime

from . import db


class PharmacyDispense(db.Model):
    __tablename__ = "pharmacy_dispenses"

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.id"), nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    notes = db.Column(db.Text, nullable=True)
    dispensed_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    medicine = db.relationship("Medicine", back_populates="dispenses")
    patient = db.relationship("Patient")

    def __repr__(self) -> str:
        return f"<PharmacyDispense {self.id}>"
