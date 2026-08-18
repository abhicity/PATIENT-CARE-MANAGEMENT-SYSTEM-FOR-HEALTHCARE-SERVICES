# PATIENT CARE MANAGEMENT SYSTEM FOR HEALTHCARE SERVICES

An integrated Flask-based hospital web application that digitizes patient care workflows across administration, consultation, diagnostics, pharmacy, billing, and reporting.

## Project Overview

This project was developed in milestones and now delivers end-to-end healthcare service operations with role-based access, secure authentication, and modular architecture.

## Tech Stack

- Python 3.12
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- Flask-Migrate
- PyMySQL
- HTML5, CSS3, Bootstrap 5, JavaScript
- SQLite (default local) and MySQL (production-ready via env variables)

## Core Features

- User registration and secure login
- Role-based dashboards and access control
- Patient CRUD and profile history
- Doctor CRUD and availability management
- Appointment scheduling and tracking
- EHR (Electronic Health Records) management
- Consultation notes and treatment workflow
- Digital prescription management
- Laboratory request and results management
- Vitals tracking (BP, pulse, temperature, respiratory rate, oxygen saturation)
- Pharmacy inventory and dispensing records
- Billing, payments, and invoice workflows
- Notification management with read/delivery state
- Feedback management
- Search, reporting, and downloadable patient summaries
- REST APIs for key modules
- Login activity auditing
- Seed data for quick demo

## Project Structure

```text
.
|-- app.py
|-- config.py
|-- forms.py
|-- helpers.py
|-- models/
|-- routes/
|-- templates/
|-- static/
|-- database/
|-- requirements.txt
|-- .gitignore
```

## Milestone Completion (1 to 4)

### Milestone 1 - Core System Foundation


- Flask project setup with modular architecture
- User authentication with password hashing
- Role-based login and redirection (Admin, Doctor, Nurse, Patient)
- Patient management module
- Doctor management module
- Appointment booking and basic dashboard
- Initial database design and integration


### Milestone 2 - EHR and Clinical Management


- EHR records module
- Consultation management module
- Prescription management module
- Laboratory reports module
- Patient medical history consolidation
- Reports and patient search module
- CRUD support for clinical records
- Seeded 5-patient clinical dataset for demonstration


### Milestone 3 - Search, Reporting, Analytics and APIs


- Advanced patient search (ID, name, phone, Aadhaar, email)
- Pharmacy inventory and dispensing workflows
- Billing and payment management
- Notification management with delivery/read tracking
- REST API blueprint (`/api/v1`) for core entities
- Dashboard analytics enhancements
- Login activity audit logging and extended RBAC


### Milestone 4 - Integrated Clinical Operations Completion


- Full hospital workflow integration across all modules
- Finalized role-based operations for Admin, Doctor, Nurse, Patient, Pharmacist, Laboratory Staff
- Vitals module fully integrated into patient monitoring flow
- End-to-end data visibility from registration to reporting
- Final report and demonstration readiness


## Setup Instructions

1. Create virtual environment:

```bash
python -m venv .venv
```

2. Activate virtual environment (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python app.py
```

## Environment Variables

- `SECRET_KEY`
- `DATABASE_URL`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_DATABASE`

If MySQL variables are not set, the app automatically uses SQLite at `database/patient_care.db`.

## Default Demo Accounts

- Admin: `admin@hospital.local` / `Admin@12345`
- Doctor: `doctor1@hospital.local` / `Doctor@12345`
- Nurse: `nurse@hospital.local` / `Nurse@12345`
- Patient: `patient1@hospital.local` / `Patient@12345`
- Pharmacist: `pharmacist@hospital.local` / `Pharma@12345`
- Laboratory Staff: `labstaff@hospital.local` / `Lab@12345`

## Role-Specific Login Routes

- Role selection: `/auth/login`
- Admin login: `/auth/login/admin`
- Doctor login: `/auth/login/doctor`
- Nurse login: `/auth/login/nurse`
- Patient login: `/auth/login/patient`
- Pharmacist login: `/auth/login/pharmacist`
- Laboratory Staff login: `/auth/login/laboratorystaff`

