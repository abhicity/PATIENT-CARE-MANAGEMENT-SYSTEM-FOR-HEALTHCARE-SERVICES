from __future__ import annotations

from datetime import date, datetime

from . import db


class Medicine(db.Model):
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True, index=True)
    category = db.Column(db.String(120), nullable=True)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, nullable=False, default=10)
    expiry_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    dispenses = db.relationship(
        "PharmacyDispense",
        back_populates="medicine",
        cascade="all, delete-orphan",
    )

    @property
    def is_low_stock(self) -> bool:
        return self.stock_quantity <= self.reorder_level

    @property
    def is_expired(self) -> bool:
        return self.expiry_date is not None and self.expiry_date < date.today()

    def __repr__(self) -> str:
        return f"<Medicine {self.name}>"
