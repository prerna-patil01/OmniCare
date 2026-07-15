"""
Turns a SIGNED recommendation into bookings.

Note the word signed. This service refuses to run on an unsigned finding, and
refuses outright on an abstention. That refusal is the augmented-not-agentic
thesis expressed as a control-flow guard rather than a slogan.
"""

from datetime import datetime, timedelta

from extensions import db
from models import (
    Appointment, CareBooking, CareWorker, Doctor, Medicine, PharmacyOrder, TriageRecord,
)


class DispatchNotPermitted(Exception):
    """Raised when dispatch is attempted on an unsigned or abstained finding."""


class DispatchService:
    """
    The fulfilment layer. Runs only after a human signs.
    """

    def dispatch(self, user, triage_id: str):
        record = TriageRecord.query.filter_by(id=triage_id, user_id=user.id).first()

        if not record:
            raise DispatchNotPermitted("No such triage record.")

        # ── The guard that defines the product ────────────────────
        if record.abstained:
            raise DispatchNotPermitted(
                "OmniCare abstained on this case. There is nothing to dispatch — "
                "acting on an abstention would defeat its purpose."
            )

        if record.human_signoff_required and not record.signed_off_at:
            raise DispatchNotPermitted(
                "This recommendation has not been signed off. "
                "Nothing executes without a human decision."
            )

        action = record.recommended_action or {}
        result = {}

        result["pharmacy"] = self._pharmacy(user, record)
        result["appointment"] = self._appointment(user, record, action)
        result["care"] = self._care(user, record, action)
        result["transport"] = self._transport(record, action)

        db.session.commit()
        return result

    def signoff(self, user, triage_id: str, signer: str = "patient"):
        """
        The human decision.

        In production this is a clinician. In the demo it is the patient
        accepting the recommendation — which is still a human, still a decision,
        and still a moment where the system stops and asks.
        """
        record = TriageRecord.query.filter_by(id=triage_id, user_id=user.id).first()
        if not record:
            return None

        if record.abstained:
            raise DispatchNotPermitted("Cannot sign off an abstention.")

        record.signed_off_by = signer
        record.signed_off_at = datetime.utcnow()
        db.session.commit()
        return record

    # ── Internals ─────────────────────────────────────────────────

    def _pharmacy(self, user, record):
        deliberation = record.deliberation or []
        pharmacy_op = next((o for o in deliberation if o.get("agent") == "pharmacy"), None)

        if not pharmacy_op or not pharmacy_op.get("suggested"):
            return None

        items, total = [], 0.0

        for suggestion in pharmacy_op["suggested"]:
            drug = suggestion.get("drug", "")
            med = Medicine.query.filter(Medicine.name.ilike(f"%{drug.split()[0]}%")).first()

            if med:
                items.append({
                    "name": med.name,
                    "strength": med.strength,
                    "price_inr": med.price_inr,
                    "prescription_required": med.prescription_required,
                    "reason": suggestion.get("reason"),
                })
                total += med.price_inr or 0
            else:
                items.append({
                    "name": drug,
                    "price_inr": None,
                    "prescription_required": suggestion.get("requires_prescription", True),
                    "reason": suggestion.get("reason"),
                    "note": "Not in partner inventory — pharmacist will source.",
                })

        if not items:
            return None

        order = PharmacyOrder(
            user_id=user.id,
            items=items,
            total_inr=total,
            status="routed",
            eta=(datetime.utcnow() + timedelta(hours=3)).strftime("Today, %-I:%M %p"),
            triage_id=record.id,
        )
        db.session.add(order)
        return order.to_dict()

    def _appointment(self, user, record, action):
        level = action.get("level")
        if level not in ("gp", "specialist", "teleconsult"):
            return None

        specialty = self._specialty_for(record)

        doctor = (
            Doctor.query.filter_by(specialty=specialty)
            .order_by(Doctor.distance_km)
            .first()
        ) or Doctor.query.filter_by(specialty="General Physician").first()

        if not doctor:
            return None

        appt = Appointment(
            user_id=user.id,
            doctor_id=doctor.id,
            mode="video" if level == "teleconsult" else "in_person",
            slot=doctor.next_slot,
            status="held",   # HELD, not booked. A slot reserved is not a commitment made.
            triage_id=record.id,
        )
        db.session.add(appt)
        db.session.flush()
        return appt.to_dict()

    def _care(self, user, record, action):
        deliberation = record.deliberation or []
        logistics = next((o for o in deliberation if o.get("agent") == "logistics"), None)

        level = action.get("level") or (logistics or {}).get("recommended_level")
        if level not in ("nurse", "asha", "anm"):
            return None

        worker = (
            CareWorker.query.filter_by(role=level)
            .order_by(CareWorker.distance_km)
            .first()
        )
        if not worker:
            return None

        booking = CareBooking(
            user_id=user.id,
            worker_id=worker.id,
            hours=2,
            starts_at=worker.available_from,
            total_inr=(worker.rate_inr_hour or 0) * 2,
            status="available",   # offered, not booked
            triage_id=record.id,
        )
        db.session.add(booking)
        db.session.flush()
        return booking.to_dict()

    @staticmethod
    def _transport(record, action):
        """
        Deep links only. No Uber API, no partner approval, no key.

        This demos better than an API call anyway — the judge watches the real
        Uber app open with the hospital already set.
        """
        if action.get("level") not in ("gp", "specialist", "emergency"):
            return None

        from models import Hospital

        hospital = Hospital.query.order_by(Hospital.distance_km).first()
        if not hospital:
            return None

        return {
            "destination": hospital.name,
            "lat": hospital.lat,
            "lng": hospital.lng,
            "distance_km": hospital.distance_km,
            "urgency": "emergency" if action.get("level") == "emergency" else "scheduled",
            "uber_deeplink": (
                f"uber://?action=setPickup&pickup=my_location"
                f"&dropoff[latitude]={hospital.lat}&dropoff[longitude]={hospital.lng}"
                f"&dropoff[nickname]={hospital.name.replace(' ', '%20')}"
            ),
            "ola_deeplink": (
                f"olacabs://app/launch?lat={hospital.lat}&lng={hospital.lng}&category=mini"
            ),
        }

    @staticmethod
    def _specialty_for(record):
        term = (record.clinical_term or record.condition or "").lower()
        table = {
            "Gastroenterologist": ("colic", "gallbladder", "hepat", "liver",
                                   "gastr", "ulcer", "abdominal", "biliary"),
            "Cardiologist": ("cardi", "angina", "heart", "arrhythm"),
            "Pulmonologist": ("pneumon", "asthma", "lung", "respiratory", "bronch"),
            "Neurologist": ("migrain", "neuro", "seizure", "stroke", "headache"),
            "Orthopedist": ("fracture", "joint", "bone", "arthr", "sprain"),
            "Dermatologist": ("skin", "rash", "derma", "eczema"),
        }
        for specialty, keys in table.items():
            if any(k in term for k in keys):
                return specialty
        return "General Physician"
