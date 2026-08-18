from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

from .appointment import Appointment  # noqa: E402
from .billing import Billing  # noqa: E402
from .consultation import Consultation  # noqa: E402
from .doctor import Doctor  # noqa: E402
from .ehr_record import EHRRecord  # noqa: E402
from .laboratory_report import LaboratoryReport  # noqa: E402
from .login_activity import LoginActivity  # noqa: E402
from .medicine import Medicine  # noqa: E402
from .notification import Notification  # noqa: E402
from .patient import Patient  # noqa: E402
from .pharmacy_dispense import PharmacyDispense  # noqa: E402
from .prescription import Prescription  # noqa: E402
from .user import User  # noqa: E402
from .vitals import Vitals  # noqa: E402
from .feedback import Feedback  # noqa: E402
