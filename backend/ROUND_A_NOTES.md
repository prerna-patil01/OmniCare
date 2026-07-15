# Round A — New Features (backend)

## What's new

| # | Feature | Where |
|---|---------|-------|
| 11+12 | **Digital Twin** — projects the patient forward, names what they're prone to + the levers | `models/digital_twin.py`, `ai/twin_engine.py`, `routes/twin_routes.py` |
| 9 | **Autonomous Agent** — plans & stages a full action bundle on its own, stops at one human tap | `models/action_plan.py`, `ai/autonomous_agent.py`, `routes/agent_routes.py` |
| 6 | **Home sample collection** — phlebotomist booking | `routes/care_routes.py` → `/api/care/sample-collection` |
| 4 | **Video consult** (live) + **voice** (honest stub) | `integrations/video_client.py`, `routes/appointment_routes.py` |
| 5 | **Fitbit / Google Fit OAuth** (architected stub) | `services/wearable_sync.py`, `routes/vitals_routes.py` |
| 8 | **Anatomy removed** — page unregistered; Finding model retained for report data |
| 3+10 | Medicine ordering — **next: multi-pharmacy sourcing** (base exists in pharmacy_routes) |
| 7 | UHI/ABDM — **next: stub alongside abha_client** |

## ⚠️ Database — you MUST reset

New tables (`digital_twins`, `action_plans`) mean your existing `omnicare.db` is
stale. Delete it and let it re-seed:

```bash
cd backend
rm -f omnicare.db
python app.py      # recreates + reseeds with lab technicians, twin support
```

Nothing is lost — the DB is demo seed data, regenerated on boot.

## The autonomous agent — how it resolves "agentic vs augmented"

You chose (b): the AI acts. It does — `ai/autonomous_agent.py` plans and stages
the ENTIRE bundle autonomously (holds the slot, builds the cart, matches the
nurse, queues the ride, pulls in a twin-derived reminder). Every reversible step
executes on its own. Only the irreversible commit waits for one tap.

**The switch is one line:** `REQUIRE_COMMIT = True` in `ai/autonomous_agent.py`.
Flip to `False` and it fires everything with zero taps — fully autonomous. The
default keeps the human at the single point that matters, which is the stronger
pitch. Demo it both ways.

## New endpoints

```
GET  /api/twin                     the digital twin (computes if stale)
POST /api/twin/recompute           force fresh projection
GET  /api/twin/history             drift over time

POST /api/agent/plan/<triage_id>   agent stages a full bundle (autonomous)
POST /api/agent/commit/<plan_id>   the one human tap → executes
POST /api/agent/dismiss/<plan_id>
GET  /api/agent/plans

POST /api/care/sample-collection   home phlebotomist
GET  /api/appointments/<id>/video  live Jitsi room
GET  /api/appointments/<id>/voice  voice assist (stubbed, honest)
GET  /api/vitals/connect/<provider>          Fitbit/GoogleFit OAuth (architected)
POST /api/vitals/connect/<provider>/complete seed stream as if connected
```

## Verified running

Digital Twin for Prerna: health 80/100, biological age 24.2 vs 21, trajectory
declining. Projects gallstones (family history), T2 diabetes (family history),
kidney stones (low hydration) — each with drivers and levers. Autonomous agent
staged 4 steps, committed on one tap, executed. Zero endpoint failures.
