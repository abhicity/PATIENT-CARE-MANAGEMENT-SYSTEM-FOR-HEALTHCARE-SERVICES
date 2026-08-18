from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import abort
from flask_login import current_user


def role_required(*roles: str) -> Callable:
    def decorator(view: Callable) -> Callable:
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped_view

    return decorator


def create_profile_for_user(user):
    if user.role == "Patient" and user.patient_profile is None:
        from models import Patient

        user.patient_profile = Patient()
    elif user.role == "Doctor" and user.doctor_profile is None:
        from models import Doctor

        user.doctor_profile = Doctor()