"""
Blueprints. One per nav item, plus the AI-heavy omni blueprint that also carries
signoff and dispatch (the human-decision step lives next to where the
recommendation was made).
"""

from .auth_routes import auth_bp
from .profile_routes import profile_bp
from .vitals_routes import vitals_bp
from .omni_routes import omni_bp
from .report_routes import report_bp
from .consent_routes import consent_bp
from .doctor_routes import doctor_bp
from .appointment_routes import appointment_bp
from .care_routes import care_bp
from .pharmacy_routes import pharmacy_bp
from .ride_routes import ride_bp
from .insurance_routes import insurance_bp
from .intelligence_routes import intelligence_bp
from .sos_routes import sos_bp
from .twin_routes import twin_bp
from .agent_routes import agent_bp

BLUEPRINTS = [
    auth_bp,
    profile_bp,
    vitals_bp,
    omni_bp,
    report_bp,
    consent_bp,
    doctor_bp,
    appointment_bp,
    care_bp,
    pharmacy_bp,
    ride_bp,
    insurance_bp,
    intelligence_bp,
    sos_bp,
    twin_bp,
    agent_bp,
]

__all__ = ["BLUEPRINTS"]
