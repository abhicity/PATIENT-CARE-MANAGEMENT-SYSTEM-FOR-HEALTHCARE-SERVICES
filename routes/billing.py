from __future__ import annotations

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from forms import BillingForm
from helpers import role_required
from models import Billing, Consultation, LaboratoryReport, Medicine, Patient, PharmacyDispense, User, db

billing_bp = Blueprint("billing", __name__, url_prefix="/billing")


def _generate_invoice_number() -> str:
    now = datetime.utcnow()
    return f"INV-{now.strftime('%Y%m%d%H%M%S%f')}"


def _default_charges(patient_id: int) -> dict[str, float]:
    consultations_count = Consultation.query.filter_by(patient_id=patient_id).count()
    laboratory_count = LaboratoryReport.query.filter_by(patient_id=patient_id).count()
    pharmacy_total = db.session.query(
        db.func.coalesce(db.func.sum(PharmacyDispense.quantity * Medicine.unit_price), 0.0)
    ).join(Medicine, Medicine.id == PharmacyDispense.medicine_id).filter(PharmacyDispense.patient_id == patient_id).scalar()
    return {
        "consultation_charge": float(consultations_count * 500),
        "laboratory_charge": float(laboratory_count * 350),
        "pharmacy_charge": float(pharmacy_total),
        "other_charge": 0.0,
    }


@billing_bp.route("/")
@login_required
@role_required("Admin", "Nurse", "Doctor", "Patient")
def list_bills():
    query = request.args.get("q", "").strip()
    bills_query = Billing.query.join(Patient, Billing.patient_id == Patient.id).outerjoin(User, Patient.user_id == User.id)
    if current_user.role == "Patient" and current_user.patient_profile:
        bills_query = bills_query.filter(Billing.patient_id == current_user.patient_profile.id)
    elif query:
        if query.isdigit():
            bills_query = bills_query.filter(Billing.patient_id == int(query))
        else:
            like_query = f"%{query}%"
            bills_query = bills_query.filter(
                (User.full_name.ilike(like_query)) | (Billing.invoice_number.ilike(like_query))
            )
    bills = bills_query.order_by(Billing.created_at.desc()).all()
    return render_template("billing/list.html", bills=bills, query=query)


@billing_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Nurse")
def create_bill():
    form = BillingForm()
    patients = Patient.query.order_by(Patient.id.asc()).all()
    if not patients:
        flash("Please add patients before creating a bill.", "warning")
        return redirect(url_for("billing.list_bills"))
    form.patient_id.choices = [(patient.id, patient.user.full_name if patient.user else f"Patient {patient.id}") for patient in patients]

    selected_patient_id = request.args.get("patient_id", type=int)
    if selected_patient_id and request.method == "GET":
        defaults = _default_charges(selected_patient_id)
        form.patient_id.data = selected_patient_id
        form.consultation_charge.data = defaults["consultation_charge"]
        form.laboratory_charge.data = defaults["laboratory_charge"]
        form.pharmacy_charge.data = defaults["pharmacy_charge"]
        form.other_charge.data = defaults["other_charge"]

    if form.validate_on_submit():
        total_amount = float(form.consultation_charge.data + form.laboratory_charge.data + form.pharmacy_charge.data + form.other_charge.data)
        bill = Billing(
            invoice_number=_generate_invoice_number(),
            patient_id=form.patient_id.data,
            consultation_charge=float(form.consultation_charge.data),
            laboratory_charge=float(form.laboratory_charge.data),
            pharmacy_charge=float(form.pharmacy_charge.data),
            other_charge=float(form.other_charge.data),
            total_amount=total_amount,
            payment_method=form.payment_method.data,
            payment_status=form.payment_status.data,
            notes=form.notes.data.strip() if form.notes.data else None,
        )
        db.session.add(bill)
        db.session.commit()
        flash("Billing invoice generated successfully.", "success")
        return redirect(url_for("billing.list_bills"))
    return render_template("billing/form.html", form=form)


@billing_bp.route("/<int:billing_id>/update-status", methods=["POST"])
@login_required
@role_required("Admin", "Nurse")
def update_payment_status(billing_id: int):
    bill = db.session.get(Billing, billing_id)
    if bill is None:
        flash("Bill not found.", "danger")
        return redirect(url_for("billing.list_bills"))
    new_status = request.form.get("payment_status", "").strip()
    if new_status not in {"Pending", "Paid", "Failed", "Refunded"}:
        flash("Invalid payment status.", "danger")
        return redirect(url_for("billing.list_bills"))
    bill.payment_status = new_status
    db.session.commit()
    flash("Payment status updated.", "success")
    return redirect(url_for("billing.list_bills"))
