from __future__ import annotations

from datetime import datetime

from . import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=True, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=True, index=True)
    title = db.Column(db.String(180), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(40), nullable=False, default="General")
    status = db.Column(db.String(20), nullable=False, default="Unread")
    delivery_status = db.Column(db.String(20), nullable=False, default="Delivered")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    read_at = db.Column(db.DateTime, nullable=True)

    patient = db.relationship("Patient", back_populates="notifications")
    doctor = db.relationship("Doctor", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification {self.id}>"
