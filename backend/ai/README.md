# OmniCare — AI Layer

Drop this folder at `backend/ai/`, replacing the existing one.

## The claim this package is built around

> An AI that cannot say "I don't know" is not safe in medicine.

Every design decision here follows from that. Six specialists deliberate
independently, they are permitted to **disagree**, and when they do the
Adjudicator **abstains** rather than averaging the disagreement away.

That is the differentiator. Every other symptom checker in the room will produce
a confident answer to every question, because producing answers is what they are
*for*. This one is allowed to refuse — and refusal, when the evidence is genuinely
ambiguous, is the correct clinical behaviour.

---

## Files

```
ai/
├── llm_client.py         Single door to Gemini. Handles the markdown-fenced-JSON
│                         problem that crashes naive parsers half the time.
├── context_builder.py    ★ The most important file. Turns a database row into a
│                         clinical brief. The difference between a chatbot and a
│                         copilot lives here.
├── orchestrator.py       Runs the MDT: consent gate → 6 parallel agents → adjudication.
├── triage_engine.py      The conversational probe. Max 6 turns, hard cap.
├── report_extractor.py   PDF/image → biomarkers. pdfplumber first, vision as fallback.
├── calibration.py        ★ Closes the Metrics loop. Scores predictions against
│                         ground truth, adjusts future confidence, TELLS THE USER.
├── population_agg.py     Layer 4 → Layer 2. Regional signals feed back into
│                         individual diagnosis. k-anonymity = 8.
│
├── agents/
│   ├── base.py           Confidence is a required field. Abstention is legitimate.
│   ├── triage_agent.py       Differentials. Resists premature closure.
│   ├── records_agent.py      History. Has ALLERGY VETO power.
│   ├── biometrics_agent.py   Wearables. Its best output is a CONTRADICTION.
│   ├── pharmacy_agent.py     Drug safety. Default answer: nothing needed.
│   ├── logistics_agent.py    Cheapest SUFFICIENT care. ASHA → nurse → GP → specialist.
│   ├── population_agent.py   Base rates. Stops the others ignoring Bayes.
│   ├── consent_agent.py  ★ Not an opinion — a GATE. Blocked agents do not run.
│   └── adjudicator.py    ★ Converge, weigh, or ABSTAIN. Has a deterministic
│                         safety layer that fires BEFORE the model.
│
└── prompts/
    ├── system.py         The constitution. Red flags. Hard boundaries.
    ├── triage_prober.py  Must ask the DISCRIMINATING question, not any question.
    ├── abstention.py     ★ When to shut up. The rubric.
    ├── adjudicator.py    How to weigh six opinions, and when not to.
    ├── agent_prompts.py  The six specialists.
    ├── report_parser.py  NEVER invent a value. Null, not zero, not an estimate.
    ├── organ_mapper.py   Finding → organ, for the anatomy hotspots.
    └── dispatch_router.py Runs only AFTER human signoff. Never before.
```

★ = the files that decide whether you win.

---

## Usage

```python
from ai import Orchestrator, ContextBuilder, TriageEngine

# 1. Build the context — this is where the product lives
builder = ContextBuilder(consent_service=consent_svc)
ctx = builder.build(
    user=user,
    profile=profile,
    history=history,
    lifestyle=lifestyle,
    vitals=vitals_last_14d,
    reports=recent_reports,
    conversation=thread,
    regional=population.context_for("Artist Village"),
)

# 2. Probe, then convene the MDT
engine = TriageEngine()
result = engine.run(user_id=user.id, context=ctx.to_prompt())

if result["phase"] == "probing":
    return result["probe"]["next_question"]

# 3. The verdict — which may be an abstention
if result["abstained"]:
    return {
        "message": result["conclusion"],
        "resolve_by": result["would_resolve_it"],
    }
```

---

## The three things that make this different

**1. The agents disagree, and the disagreement is shown.**
Triage says gallstones. Population says dengue is up 12% locally and causes
hepatitis with exactly that pain. Biometrics says resting HR is up 8% over three
days. Records says no fever logged.

They *conflict*. The Adjudicator sees it and refuses to pick — and says exactly
what would settle it: *"Take your temperature in the next six hours."*

**2. Consent is a gate, not a checkbox.**
`ConsentAgent` runs before any agent sees any data. Blocked agents don't run with
less data — they don't run. Every check is logged, granted or denied, so "who saw
my liver panel and when" has a complete answer.

**3. Calibration closes the loop.**
When the ultrasound comes back, `Calibrator` scores what Omni predicted against
what was true, and marks down future confidence in that domain — *and tells the
user it's doing so.* An AI that quietly corrects itself is a black box. One that
says "I've been over-weighting post-prandial pain in your case" is a colleague.

---

## Environment

```bash
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.0-flash
```

Without a key the LLM client runs in **mock mode** — the app still boots, so the
frontend is never blocked and a rate limit can't kill your demo.

## Dependencies

```
google-generativeai>=0.7.0
pdfplumber>=0.11.0
Pillow>=10.0.0
```

Nothing else. No LangChain, no agent framework. Those abstractions hide the
reasoning, and a Healthcare OS that can't explain itself is worthless.
