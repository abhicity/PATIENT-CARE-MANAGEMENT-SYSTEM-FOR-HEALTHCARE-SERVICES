from __future__ import annotations

from datetime import datetime

from . import db


class Billing(db.Model):
    __tablename__ = "billings"

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(40), nullable=False, unique=True, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    consultation_charge = db.Column(db.Float, nullable=False, default=0.0)
    laboratory_charge = db.Column(db.Float, nullable=False, default=0.0)
    pharmacy_charge = db.Column(db.Float, nullable=False, default=0.0)
    other_charge = db.Column(db.Float, nullable=False, default=0.0)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    payment_method = db.Column(db.String(30), nullable=False, default="Cash")
    payment_status = db.Column(db.String(30), nullable=False, default="Pending")
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    patient = db.relationship("Patient", back_populates="billings")

    def __repr__(self) -> str:
        return f"<Billing {self.invoice_number}>"
