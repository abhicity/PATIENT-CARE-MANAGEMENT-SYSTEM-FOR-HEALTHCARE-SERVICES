from __future__ import annotations

from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from forms import DispenseMedicineForm, MedicineForm
from helpers import role_required
from models import Medicine, Patient, PharmacyDispense, db

pharmacy_bp = Blueprint("pharmacy", __name__, url_prefix="/pharmacy")


@pharmacy_bp.route("/")
@login_required
@role_required("Admin", "Pharmacist", "Doctor", "Nurse")
def list_inventory():
    query = request.args.get("q", "").strip()
    medicines_query = Medicine.query
    if query:
        like_query = f"%{query}%"
        medicines_query = medicines_query.filter(
            (Medicine.name.ilike(like_query)) | (Medicine.category.ilike(like_query))
        )
    medicines = medicines_query.order_by(Medicine.name.asc()).all()
    low_stock_count = sum(1 for item in medicines if item.is_low_stock)
    expired_count = sum(1 for item in medicines if item.is_expired)
    dispensed_today = PharmacyDispense.query.filter(
        db.func.date(PharmacyDispense.dispensed_on) == date.today()
    ).count()
    return render_template(
        "pharmacy/list.html",
        medicines=medicines,
        query=query,
        low_stock_count=low_stock_count,
        expired_count=expired_count,
        dispensed_today=dispensed_today,
    )


@pharmacy_bp.route("/add", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Pharmacist")
def add_medicine():
    form = MedicineForm()
    if form.validate_on_submit():
        existing = Medicine.query.filter(db.func.lower(Medicine.name) == form.name.data.lower().strip()).first()
        if existing:
            flash("Medicine already exists. Use edit to update stock.", "warning")
            return redirect(url_for("pharmacy.list_inventory"))
        medicine = Medicine(
            name=form.name.data.strip(),
            category=form.category.data.strip() if form.category.data else None,
            unit_price=float(form.unit_price.data),
            stock_quantity=form.stock_quantity.data,
            reorder_level=form.reorder_level.data,
            expiry_date=form.expiry_date.data,
        )
        db.session.add(medicine)
        db.session.commit()
        flash("Medicine added to inventory.", "success")
        return redirect(url_for("pharmacy.list_inventory"))
    return render_template("pharmacy/form.html", form=form, title="Add Medicine")


@pharmacy_bp.route("/<int:medicine_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Pharmacist")
def edit_medicine(medicine_id: int):
    medicine = db.session.get(Medicine, medicine_id)
    if medicine is None:
        flash("Medicine not found.", "danger")
        return redirect(url_for("pharmacy.list_inventory"))
    form = MedicineForm(obj=medicine)
    if form.validate_on_submit():
        medicine.name = form.name.data.strip()
        medicine.category = form.category.data.strip() if form.category.data else None
        medicine.unit_price = float(form.unit_price.data)
        medicine.stock_quantity = form.stock_quantity.data
        medicine.reorder_level = form.reorder_level.data
        medicine.expiry_date = form.expiry_date.data
        db.session.commit()
        flash("Medicine inventory updated.", "success")
        return redirect(url_for("pharmacy.list_inventory"))
    return render_template("pharmacy/form.html", form=form, title="Edit Medicine")


@pharmacy_bp.route("/dispense", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Pharmacist")
def dispense_medicine():
    form = DispenseMedicineForm()
    medicines = Medicine.query.order_by(Medicine.name.asc()).all()
    patients = Patient.query.order_by(Patient.id.asc()).all()
    if not medicines or not patients:
        flash("Add medicines and patients before dispensing.", "warning")
        return redirect(url_for("pharmacy.list_inventory"))
    form.medicine_id.choices = [(medicine.id, f"{medicine.name} (Stock: {medicine.stock_quantity})") for medicine in medicines]
    form.patient_id.choices = [(patient.id, patient.user.full_name if patient.user else f"Patient {patient.id}") for patient in patients]

    if form.validate_on_submit():
        medicine = db.session.get(Medicine, form.medicine_id.data)
        if medicine is None:
            flash("Medicine not found.", "danger")
            return redirect(url_for("pharmacy.dispense_medicine"))
        if medicine.stock_quantity < form.quantity.data:
            flash("Insufficient stock for this medicine.", "danger")
            return redirect(url_for("pharmacy.dispense_medicine"))

        medicine.stock_quantity -= form.quantity.data
        dispense = PharmacyDispense(
            medicine_id=medicine.id,
            patient_id=form.patient_id.data,
            quantity=form.quantity.data,
            notes=form.notes.data.strip() if form.notes.data else None,
        )
        db.session.add(dispense)
        db.session.commit()
        flash("Medicine dispensed successfully.", "success")
        return redirect(url_for("pharmacy.dispense_history"))
    return render_template("pharmacy/dispense_form.html", form=form)


@pharmacy_bp.route("/dispenses")
@login_required
@role_required("Admin", "Pharmacist", "Doctor", "Nurse", "Patient")
def dispense_history():
    dispenses_query = PharmacyDispense.query.order_by(PharmacyDispense.dispensed_on.desc())
    if current_user.role == "Patient" and current_user.patient_profile:
        dispenses_query = dispenses_query.filter(PharmacyDispense.patient_id == current_user.patient_profile.id)
    dispenses = dispenses_query.limit(200).all()
    return render_template("pharmacy/dispenses.html", dispenses=dispenses)
