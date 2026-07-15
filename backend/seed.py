"""
Seed data.

The demo patient is not arbitrary. Her wearable stream contains a REAL rising
heart rate and falling HRV — a febrile response she has not consciously noticed.
Her region has a dengue signal. Her symptoms fit gallstones.

Which means when the agents deliberate, they will GENUINELY disagree:

    Triage      → biliary colic, most likely
    Population  → dengue is up locally, and it causes hepatitis with the same pain
    Biometrics  → resting HR up 8% over 3 days, HRV down — she is mounting a fever
    Records     → but she has logged no fever

    Adjudicator → ABSTAIN. Take your temperature.

The demo works because the data actually contains the thing the AI claims to find.
A demo where the signal is asserted rather than present is a lie with extra steps.
"""

from datetime import date, datetime, timedelta

from extensions import db
from models import (
    CareWorker, ConsentPurpose, ConsentScope, Doctor, HealthProfile, Hospital,
    InsurancePolicy, Lifestyle, Medicine, MedicalHistory, TriageRecord, User,
)
from services import ConsentService, WearableSync


def seed_all():
    if User.query.first():
        return  # already seeded

    print("  Seeding…")

    user = _demo_user()
    _doctors()
    _care_workers()
    _hospitals()
    _medicines()
    _population_signal(user.region)

    print("  Seeded. Demo user: prerna@omnicare.health")


def _demo_user():
    user = User(
        name="Prerna Patil",
        email="prerna@omnicare.health",
        phone="9876543210",
        abha_id="12-3456-7890-1234",
        region="Artist Village",
        onboarded=True,
    )
    db.session.add(user)
    db.session.flush()

    db.session.add(HealthProfile(
        user_id=user.id,
        dob=date(2004, 8, 14),
        gender="Female",
        height_cm=165,
        weight_kg=56,
        blood_group="B+",
        emergency_contact="9876500000",
    ))

    db.session.add(MedicalHistory(
        user_id=user.id,
        allergies=["Penicillin", "Dust mites"],
        current_diseases=[],
        past_diseases=["Dengue (2021)"],   # prior dengue — the Population agent will notice
        surgeries=[],
        medications=[],
        family_history=["Gallstones (mother)", "Type 2 diabetes (father)"],
        vaccinations=["COVID-19", "Hepatitis B", "Typhoid"],
    ))

    db.session.add(Lifestyle(
        user_id=user.id,
        smoking="Never",
        alcohol="Socially",
        food_habits="Vegetarian",
        exercise="1–2 × week",
        stress="High",
        sleep="6-7",
        hydration_l=1.2,       # chronically low — a real finding
        occupation="Student",
    ))

    db.session.commit()

    ConsentService.bootstrap(user.id)
    WearableSync.seed_stream(user.id, days=14)

    db.session.add(InsurancePolicy(
        user_id=user.id,
        provider="Star Health",
        policy_number="STAR-88213456",
        policy_type="family_floater",
        sum_insured_inr=500000,
        used_inr=42000,
        valid_till="2027-03-31",
        cashless=True,
    ))
    db.session.commit()

    return user


def _doctors():
    rows = [
        ("Dr. Anjali Menon", "Gastroenterologist", "MD, DM (Gastro)", "Apollo Hospitals",
         14, 4.8, 312, 900, 19.0330, 73.0297, 2.4, "Tomorrow, 10:30 AM",
         ["English", "Hindi", "Marathi"]),
        ("Dr. Rakesh Iyer", "Gastroenterologist", "MBBS, MS", "Fortis Hiranandani",
         9, 4.6, 198, 750, 19.0450, 73.0180, 4.1, "Tomorrow, 2:00 PM",
         ["English", "Hindi"]),
        ("Dr. Sneha Kulkarni", "General Physician", "MBBS", "Lifeline Clinic",
         7, 4.7, 421, 400, 19.0290, 73.0350, 1.1, "Today, 6:30 PM",
         ["English", "Hindi", "Marathi"]),
        ("Dr. Vikram Desai", "General Physician", "MBBS, MD", "Sanjeevani Polyclinic",
         12, 4.5, 267, 500, 19.0310, 73.0400, 1.8, "Today, 7:00 PM",
         ["English", "Marathi"]),
        ("Dr. Farah Sheikh", "Cardiologist", "MD, DM (Cardio)", "Apollo Hospitals",
         18, 4.9, 508, 1200, 19.0330, 73.0297, 2.4, "Thursday, 11:00 AM",
         ["English", "Hindi", "Urdu"]),
        ("Dr. Nikhil Rao", "Pulmonologist", "MBBS, MD (Pulm)", "Fortis Hiranandani",
         11, 4.6, 156, 850, 19.0450, 73.0180, 4.1, "Wednesday, 3:30 PM",
         ["English", "Hindi"]),
    ]

    for r in rows:
        db.session.add(Doctor(
            name=r[0], specialty=r[1], qualification=r[2], hospital=r[3],
            experience_years=r[4], rating=r[5], review_count=r[6], fee_inr=r[7],
            lat=r[8], lng=r[9], distance_km=r[10], next_slot=r[11], languages=r[12],
            video_available=True,
        ))
    db.session.commit()


def _care_workers():
    """
    The moat. Nurses, ASHA workers, ANMs, physios.

    Note the rates. An ASHA worker at ₹180/hr versus a specialist at ₹900 is not
    a small difference — it is the difference between care that happens and care
    that gets postponed indefinitely.
    """
    rows = [
        ("Sr. Kavitha Rao", "nurse", 8, 4.9, 340, 1.2, "Now",
         ["Hindi", "Marathi", "English"],
         ["IV administration", "Wound dressing", "Injections", "Post-op care"]),
        ("Sr. Meera Joshi", "nurse", 5, 4.7, 300, 2.6, "In 2 hours",
         ["Hindi", "Marathi"],
         ["Injections", "Vitals monitoring", "Elderly care"]),
        ("Lakshmi Devi", "asha", 11, 4.8, 180, 0.8, "Tomorrow, 9 AM",
         ["Marathi", "Hindi"],
         ["Maternal care", "Child vaccination", "Home visits", "Health education"]),
        ("Sunita Pawar", "asha", 6, 4.6, 180, 1.5, "Tomorrow, 11 AM",
         ["Marathi"],
         ["Pregnancy monitoring", "Immunisation", "Government scheme enrolment"]),
        ("Anita Kamble", "anm", 9, 4.7, 220, 2.1, "Today, 5 PM",
         ["Marathi", "Hindi"],
         ["Midwifery", "Antenatal care", "Family planning"]),
        ("Rahul Bhosale", "physio", 7, 4.8, 450, 3.0, "Tomorrow, 4 PM",
         ["English", "Marathi"],
         ["Post-surgical rehab", "Sports injury", "Back pain"]),
        ("Deepa Nair", "dietician", 6, 4.9, 400, 2.2, "Wednesday",
         ["English", "Hindi", "Malayalam"],
         ["PCOS", "Diabetes", "Weight management", "Gut health"]),
        ("Ramesh Yadav", "caretaker", 12, 4.5, 200, 1.9, "Now",
         ["Hindi", "Marathi"],
         ["Elderly care", "Dementia support", "Home assistance"]),
        ("Ravi Teja", "lab_technician", 5, 4.7, 250, 1.4, "Today, 6 AM",
         ["Hindi", "Telugu", "English"],
         ["Home blood collection", "Sample pickup", "ECG at home"]),
        ("Priya Menon", "lab_technician", 8, 4.9, 280, 2.0, "Tomorrow, 7 AM",
         ["English", "Malayalam", "Hindi"],
         ["Home blood collection", "Urine sample", "Swab collection"]),
    ]

    for r in rows:
        db.session.add(CareWorker(
            name=r[0], role=r[1], experience_years=r[2], rating=r[3],
            rate_inr_hour=r[4], distance_km=r[5], available_from=r[6],
            languages=r[7], services=r[8], verified=True,
        ))
    db.session.commit()


def _hospitals():
    rows = [
        ("Apollo Hospitals, Navi Mumbai", 19.0330, 73.0297, 2.4, 68, True,
         ["Emergency", "Gastroenterology", "Cardiology", "Oncology"]),
        ("Fortis Hiranandani", 19.0450, 73.0180, 4.1, 52, True,
         ["Emergency", "Orthopedics", "Neurology", "Pulmonology"]),
        ("MGM Hospital, Vashi", 19.0760, 73.0000, 6.8, 81, True,
         ["Emergency", "General Medicine", "Paediatrics"]),
    ]

    for r in rows:
        db.session.add(Hospital(
            name=r[0], lat=r[1], lng=r[2], distance_km=r[3],
            er_load_pct=r[4], cashless=r[5], specialties=r[6],
        ))
    db.session.commit()


def _medicines():
    rows = [
        ("Pantoprazole 40mg", "Pantoprazole", "Tablet", "40mg", 88.0, True, "Today, 7:40 PM"),
        ("ORS Sachets", "Oral Rehydration Salts", "Sachet", "21.8g", 24.0, False, "Today, 7:40 PM"),
        ("Paracetamol 650mg", "Paracetamol", "Tablet", "650mg", 32.0, False, "Today, 7:40 PM"),
        ("Drotaverine 40mg", "Drotaverine", "Tablet", "40mg", 76.0, True, "Tomorrow, 10 AM"),
        ("Ursodeoxycholic Acid 300mg", "UDCA", "Tablet", "300mg", 340.0, True, "Tomorrow, 10 AM"),
        ("Domperidone 10mg", "Domperidone", "Tablet", "10mg", 54.0, True, "Today, 7:40 PM"),
    ]

    for r in rows:
        db.session.add(Medicine(
            name=r[0], generic=r[1], form=r[2], strength=r[3],
            price_inr=r[4], prescription_required=r[5],
            in_stock=True, delivery_eta=r[6],
        ))
    db.session.commit()


def _population_signal(region):
    """
    Seed a dengue signal in the region.

    Not decoration. The Population Agent will pick this up and raise dengue
    hepatitis as a differential the Triage agent did not consider — which is what
    triggers the disagreement, which is what triggers the abstention, which is
    the entire demo.

    12 cases, which clears the k-anonymity threshold of 8.
    """
    now = datetime.utcnow()

    # Current window — dengue is spiking
    for i in range(12):
        db.session.add(TriageRecord(
            condition="dengue",
            region=region,
            decision="converge",
            confidence=0.7,
            risk_score=6.0,
            risk_band="medium",
            created_at=now - timedelta(days=i % 6, hours=i),
        ))

    # Baseline window — it was not spiking six weeks ago
    for i in range(3):
        db.session.add(TriageRecord(
            condition="dengue",
            region=region,
            decision="converge",
            confidence=0.6,
            risk_score=5.0,
            risk_band="medium",
            created_at=now - timedelta(days=30 + i * 3),
        ))

    # Some background noise so dengue's rise is measured against something
    for condition, n in [("viral fever", 22), ("gastroenteritis", 9), ("migraine", 6)]:
        for i in range(n):
            db.session.add(TriageRecord(
                condition=condition,
                region=region,
                decision="converge",
                confidence=0.65,
                risk_score=3.0,
                risk_band="low",
                created_at=now - timedelta(days=i % 40, hours=i),
            ))

    db.session.commit()
