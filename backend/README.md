# OmniCare — Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # add your keys
python app.py             # → http://localhost:5000
```

Boots, creates the DB, seeds itself. No login required in demo mode.

Check it's alive: `curl localhost:5000/api/health`

---

## The demo that wins

The seed data is not decorative. It is **engineered so the agents genuinely disagree.**

Prerna's record contains:
- Symptoms consistent with **gallstones** (family history: gallstones, mother)
- A wearable stream with **resting HR up 6%, HRV down 11%** over 14 days — a febrile response she has not consciously noticed
- A region where **dengue is up 150%** (12 cases, above the k-anonymity threshold)
- **Prior dengue in 2021**
- **No fever logged**

So when you POST to `/api/omni/chat`:

```
TRIAGE      → biliary colic, 0.72
POPULATION  → dengue up 150% locally, causes hepatitis with the same RUQ pain
BIOMETRICS  → HR climbing, HRV falling — she is mounting a fever she hasn't felt
RECORDS     → but no fever is logged, and she had dengue in 2021
─────────────────────────────────────────────────────────────────
ADJUDICATOR → ABSTAIN. Two paths remain open. Take your temperature
              in the next six hours. If it's above 38, this changes.
```

**No other team's AI will refuse to answer.** That is the entire pitch.

---

## The three files that matter

| File | Why |
|---|---|
| `ai/context_builder.py` | Turns a database row into a clinical brief. The difference between a chatbot and a copilot. |
| `ai/agents/consent_agent.py` | A **gate**, not a checkbox. Blocked agents don't run with less data — they don't run. |
| `ai/agents/adjudicator.py` | Has a **deterministic safety layer that fires before the model.** A safety property that depends on the model choosing to be safe is not a safety property. |

---

## Endpoints

**Omni** — the product
```
POST /api/omni/chat              probe or conclude. May abstain.
GET  /api/omni/findings          latest verdict (dashboard hero)
GET  /api/omni/calibration       how honest has Omni been, for you, over time
POST /api/omni/outcome/<id>      ground truth → closes the Metrics loop
```

**Consent** — the differentiator
```
GET  /api/consent/ledger         every grant, scoped and expiring
GET  /api/consent/audit          every access, granted AND denied
POST /api/consent/grant
POST /api/consent/revoke/<id>    ← the demo moment
```

**The rest**
```
POST /api/profile/onboard        4-step onboarding + seeds wearable stream
GET  /api/vitals                 latest + 14-day trend
POST /api/reports/upload         PDF/image → biomarkers → pinned to an organ
GET  /api/anatomy/findings       what makes the liver glow red
GET  /api/doctors                filter by specialty, fee, distance
GET  /api/care/workers           nurses · ASHA · ANM — the moat
GET  /api/intelligence/regional  Layer 4, k-anonymity ≥ 8
POST /api/dispatch/signoff/<id>  ← the human decision. Nothing moves without it.
POST /api/dispatch/<id>          fan out to pharmacy, ride, nurse
POST /api/sos/trigger            emergency override + audit
```

---

## Live the revoke demo

```bash
# 1. Show the ledger
curl localhost:5000/api/consent/ledger

# 2. Revoke medical history
curl -X POST localhost:5000/api/consent/revoke/<grant_id> \
  -H 'Content-Type: application/json' \
  -d '{"reason":"I changed my mind"}'

# 3. Ask Omni again — the Records and Pharmacy agents no longer run,
#    and the response says so in consent_blocks[]
curl -X POST localhost:5000/api/omni/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"pain in my upper right abdomen"}'
```

The AI visibly becomes less capable, and **tells you why.** That is what consent
actually means, and nobody else in the room will be able to show it.

---

## Honest notes

- **Apple Health has no web API.** HealthKit is iOS-native; a React web app fundamentally cannot read it. The wearable stream is synthetic — but the *signal inside it is real*, which is what makes the demo work.
- **Uber/Ola use deep links**, not APIs. Partner approval takes months. The deep link opens the real app with the hospital pre-filled — which demos *better* than a JSON response claiming a ride was booked.
- **Auth is passwordless.** Real JWT, real tokens, but no OTP verification. Nobody will test your login.
- **Without `GEMINI_API_KEY`** the AI runs in mock mode. The app still boots — a rate limit at 4pm on demo day should not be able to kill your product.
