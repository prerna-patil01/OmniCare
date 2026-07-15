"""
Pharmacy fulfilment.

1mg, PharmEasy, Netmeds — none expose a public ordering API; all are partner-
gated. For the demo, orders resolve against the seeded Medicine directory and
are marked 'routed'. The rails are here; the live partner handshake is not.
"""

from models import Medicine


def match(drug_name: str):
    """Find the closest seeded medicine to a suggested drug name."""
    if not drug_name:
        return None
    head = drug_name.split()[0]
    return Medicine.query.filter(Medicine.name.ilike(f"%{head}%")).first()
