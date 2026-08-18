from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange, Optional, Regexp


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Regexp(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", message="Enter a valid email address."), Length(max=150)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email", validators=[DataRequired(), Regexp(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", message="Enter a valid email address."), Length(max=150)])
    phone = StringField(
        "Phone Number",
        validators=[DataRequired(), Regexp(r"^[0-9+()\-\s]{7,20}$", message="Enter a valid phone number.")],
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    role = SelectField(
        "Role",
        choices=[
            ("Admin", "Admin"),
            ("Doctor", "Doctor"),
            ("Nurse", "Nurse"),
            ("Patient", "Patient"),
            ("Pharmacist", "Pharmacist"),
            ("LaboratoryStaff", "Laboratory Staff"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Create Account")


class PatientForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email", validators=[DataRequired(), Regexp(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", message="Enter a valid email address."), Length(max=150)])
    phone = StringField(
        "Phone Number",
        validators=[DataRequired(), Regexp(r"^[0-9+()\-\s]{7,20}$", message="Enter a valid phone number.")],
    )
    age = StringField("Age", validators=[Optional(), Regexp(r"^[0-9]{1,3}$", message="Age must be numeric.")])
    gender = SelectField(
        "Gender",
        choices=[("", "Select"), ("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
        validators=[Optional()],
    )
    aadhaar_number = StringField(
        "Aadhaar Number",
        validators=[Optional(), Regexp(r"^[0-9]{12}$", message="Aadhaar must be 12 digits.")],
    )
    blood_group = StringField("Blood Group", validators=[Optional(), Length(max=10)])
    address = TextAreaField("Address", validators=[Optional(), Length(max=500)])
    medical_history = TextAreaField("Medical History", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Save Patient")


class DoctorForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField("Email", validators=[DataRequired(), Regexp(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", message="Enter a valid email address."), Length(max=150)])
    phone = StringField(
        "Phone Number",
        validators=[DataRequired(), Regexp(r"^[0-9+()\-\s]{7,20}$", message="Enter a valid phone number.")],
    )
    specialization = SelectField(
        "Specialization",
        choices=[
            ("", "Select Specialization"),
            ("General Medicine", "General Medicine"),
            ("Cardiology", "Cardiology"),
            ("Pediatrics", "Pediatrics"),
            ("Orthopedics", "Orthopedics"),
            ("Gynecology", "Gynecology"),
            ("Cardiologist", "Cardiologist"),
            ("Neurologist", "Neurologist"),
            ("Orthopedic", "Orthopedic"),
            ("Pediatrician", "Pediatrician"),
            ("Dermatologist", "Dermatologist"),
            ("General Physician", "General Physician"),
            ("Gynecologist", "Gynecologist"),
            ("ENT Specialist", "ENT Specialist"),
        ],
        validators=[Optional()],
    )
    qualification = StringField("Qualification", validators=[Optional(), Length(max=120)])
    department = SelectField(
        "Department",
        choices=[
            ("", "Select Department"),
            ("Medicine", "Medicine"),
            ("Cardiology", "Cardiology"),
            ("Neurology", "Neurology"),
            ("Orthopedics", "Orthopedics"),
            ("Pediatrics", "Pediatrics"),
            ("Dermatology", "Dermatology"),
            ("General Medicine", "General Medicine"),
            ("Gynecology", "Gynecology"),
            ("ENT", "ENT"),
        ],
        validators=[Optional()],
    )
    available_time = StringField("Available Time", validators=[Optional(), Length(max=120)])
    submit = SubmitField("Save Doctor")


class AppointmentForm(FlaskForm):
    patient_id = SelectField("Patient", coerce=int, validators=[DataRequired()])
    doctor_id = SelectField("Doctor", coerce=int, validators=[DataRequired()])
    appointment_date = DateField("Appointment Date", validators=[DataRequired()], format="%Y-%m-%d")
    appointment_time = TimeField("Appointment Time", validators=[DataRequired()], format="%H:%M")
    status = SelectField(
        "Status",
        choices=[("Pending", "Pending"), ("Confirmed", "Confirmed"), ("Completed", "Completed"), ("Cancelled", "Cancelled")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Book Appointment")


class SearchForm(FlaskForm):
    query = StringField("Search", validators=[Optional(), Length(max=150)])
    submit = SubmitField("Search")


class EHRForm(FlaskForm):
    patient_id = SelectField("Patient", coerce=int, validators=[DataRequired()])
    diagnosis_details = TextAreaField("Diagnosis Details", validators=[Optional(), Length(max=2000)])
    allergies = TextAreaField("Allergies", validators=[Optional(), Length(max=1000)])
    medications = TextAreaField("Medications", validators=[Optional(), Length(max=2000)])
    notes = TextAreaField("Clinical Notes", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Save EHR")


class ConsultationForm(FlaskForm):
    patient_id = SelectField("Patient", coerce=int, validators=[DataRequired()])
    doctor_id = SelectField("Doctor", coerce=int, validators=[DataRequired()])
    consultation_date = DateField("Consultation Date", validators=[DataRequired()], format="%Y-%m-%d")
    symptoms = TextAreaField("Symptoms", validators=[DataRequired(), Length(max=2000)])
    diagnosis = TextAreaField("Diagnosis", validators=[DataRequired(), Length(max=2000)])
    treatment_notes = TextAreaField("Treatment/Prescription", validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField("Save Consultation")


class VitalsForm(FlaskForm):
    patient_id = SelectField("Patient", coerce=int, validators=[DataRequired()])
    recorded_by_id = SelectField("Recorded By", coerce=int, validators=[DataRequired()])
    blood_pressure_systolic = IntegerField("Systolic BP", validators=[Optional(), NumberRange(min=0)])
    blood_pressure_diastolic = IntegerField("Diastolic BP", validators=[Optional(), NumberRange(min=0)])
    pulse_rate = IntegerField("Pulse Rate", validators=[Optional(), NumberRange(min=0)])
    temperature_c = DecimalField("Temperature (°C)", validators=[Optional(), NumberRange(min=0)], places=1)
    respiratory_rate = IntegerField("Respiratory Rate", validators=[Optional(), NumberRange(min=0)])
    oxygen_saturation = IntegerField("Oxygen Saturation (%)", validators=[Optional(), NumberRange(min=0, max=100)])
    notes = TextAreaField("Clinical Notes", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Save Vitals")


class PrescriptionForm(FlaskForm):
    patient_id = SelectField("Patient", coerce=int, validators=[DataRequired()])
    doctor_id = SelectField("Doctor", coerce=int, validators=[DataRequired()])
    prescribed_on = DateField("Prescription Date", validators=[DataRequired()], format="%Y-%m-%d")
    medicine_name = StringField("Medicine Name", validators=[DataRequired(), Length(max=150)])
    dosage = StringField("Dosage", validators=[DataRequired(), Length(max=120)])
    frequency = StringField("Frequency", validators=[DataRequired(), Length(max=120)])
    duration = StringField("Duration", validators=[DataRequired(), Length(max=120)])
    special_instructions = TextAreaField("Special Instructions", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Save Prescription")


class LaboratoryReportForm(FlaskForm):
    patient_id = SelectField("Patient", coerce=int, validators=[DataRequired()])
    doctor_id = SelectField("Doctor", coerce=int, validators=[DataRequired()])
    test_type = SelectField(
        "Laboratory Test Type",
        choices=[
            ("Blood Test", "Blood Test"),
            ("Urine Test", "Urine Test"),
            ("X-Ray", "X-Ray"),
            ("MRI", "MRI"),
            ("CT Scan", "CT Scan"),
            ("Ultrasound", "Ultrasound"),
            ("ECG", "ECG"),
            ("Other", "Other"),
        ],
        validators=[DataRequired()],
    )
    test_date = DateField("Test Date", validators=[DataRequired()], format="%Y-%m-%d")
    result = TextAreaField("Laboratory Test Result", validators=[DataRequired(), Length(max=2000)])
    remarks = TextAreaField("Remarks/Observations", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Save Laboratory Report")


class PatientHistorySearchForm(FlaskForm):
    patient_query = StringField(
        "Patient ID, Name, Phone, Aadhaar, or Email",
        validators=[DataRequired(), Length(max=150)],
    )
    submit = SubmitField("Search")


class MedicineForm(FlaskForm):
    name = StringField("Medicine Name", validators=[DataRequired(), Length(max=150)])
    category = StringField("Category", validators=[Optional(), Length(max=120)])
    unit_price = DecimalField("Unit Price", validators=[DataRequired(), NumberRange(min=0)], places=2)
    stock_quantity = IntegerField("Stock Quantity", validators=[DataRequired(), NumberRange(min=0)])
    reorder_level = IntegerField("Low Stock Threshold", validators=[DataRequired(), NumberRange(min=0)])
    expiry_date = DateField("Expiry Date", validators=[Optional()], format="%Y-%m-%d")
    submit = SubmitField("Save Medicine")


class DispenseMedicineForm(FlaskForm):
    medicine_id = SelectField("Medicine", coerce=int, validators=[DataRequired()])
    patient_id = SelectField("Patient", coerce=int, validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=1)])
    notes = TextAreaField("Dispense Notes", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Dispense Medicine")


class BillingForm(FlaskForm):
    patient_id = SelectField("Patient", coerce=int, validators=[DataRequired()])
    consultation_charge = DecimalField("Consultation Charge", validators=[DataRequired(), NumberRange(min=0)], places=2)
    laboratory_charge = DecimalField("Laboratory Charge", validators=[DataRequired(), NumberRange(min=0)], places=2)
    pharmacy_charge = DecimalField("Pharmacy Charge", validators=[DataRequired(), NumberRange(min=0)], places=2)
    other_charge = DecimalField("Other Charge", validators=[DataRequired(), NumberRange(min=0)], places=2)
    payment_method = SelectField(
        "Payment Method",
        choices=[("Cash", "Cash"), ("Card", "Card"), ("UPI", "UPI"), ("NetBanking", "Net Banking")],
        validators=[DataRequired()],
    )
    payment_status = SelectField(
        "Payment Status",
        choices=[("Pending", "Pending"), ("Paid", "Paid"), ("Failed", "Failed"), ("Refunded", "Refunded")],
        validators=[DataRequired()],
    )
    notes = TextAreaField("Billing Notes", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Generate Invoice")


class NotificationForm(FlaskForm):
    patient_id = SelectField("Patient (Optional)", coerce=int, validators=[Optional()])
    doctor_id = SelectField("Doctor (Optional)", coerce=int, validators=[Optional()])
    notification_type = SelectField(
        "Notification Type",
        choices=[
            ("Appointment", "Appointment Reminder"),
            ("Laboratory", "Laboratory Update"),
            ("Prescription", "Prescription Ready"),
            ("Billing", "Billing Reminder"),
            ("General", "General Announcement"),
        ],
        validators=[DataRequired()],
    )
    title = StringField("Title", validators=[DataRequired(), Length(max=180)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=2000)])
    delivery_status = SelectField(
        "Delivery Status",
        choices=[("Delivered", "Delivered"), ("Queued", "Queued"), ("Failed", "Failed")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Send Notification")


class PatientFeedbackForm(FlaskForm):
    patient_id = SelectField("Patient", coerce=int, validators=[DataRequired()])
    doctor_id = SelectField("Doctor", coerce=int, validators=[Optional()])
    consultation_rating = SelectField("Consultation Rating", coerce=int, choices=[(5, "5"), (4, "4"), (3, "3"), (2, "2"), (1, "1")], validators=[DataRequired()])
    doctor_rating = SelectField("Doctor Rating", coerce=int, choices=[(5, "5"), (4, "4"), (3, "3"), (2, "2"), (1, "1")], validators=[DataRequired()])
    hospital_service_rating = SelectField("Hospital Service Rating", coerce=int, choices=[(5, "5"), (4, "4"), (3, "3"), (2, "2"), (1, "1")], validators=[DataRequired()])
    laboratory_service_rating = SelectField("Laboratory Service Rating", coerce=int, choices=[(5, "5"), (4, "4"), (3, "3"), (2, "2"), (1, "1")], validators=[DataRequired()])
    pharmacy_service_rating = SelectField("Pharmacy Service Rating", coerce=int, choices=[(5, "5"), (4, "4"), (3, "3"), (2, "2"), (1, "1")], validators=[DataRequired()])
    comments = TextAreaField("Comments", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Submit Feedback")

