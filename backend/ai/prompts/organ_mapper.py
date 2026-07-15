"""
Maps a clinical finding to an anatomical location.

This is what makes the body light up. A finding without a location is a line of
text; a finding pinned to an organ is a diagram of what is happening inside you.
"""

ORGAN_MAPPER = """{core_system}

ROLE: Map a clinical finding to the organ system it implicates.

Available organs (use these exact strings, lowercase):
  brain, heart, lungs, liver, gallbladder, stomach, pancreas, kidneys,
  intestines, spleen, thyroid, skin, bones, joints, muscles, blood

If a finding is systemic (sepsis, anaemia, an electrolyte disturbance), return
"blood" — it is the closest honest answer, and it is better than arbitrarily
picking one organ to blame.

If you cannot map it with reasonable confidence, return null. A dot on the wrong
organ is worse than no dot: it tells the patient something false about their own
body, and they will believe it.

FINDING: {finding}
CLINICAL TERM: {clinical_term}
RISK BAND: {risk_band}

Return ONLY valid JSON:
{{
  "organ": "string from the list, or null",
  "secondary_organs": ["others also implicated"] or [],
  "severity": "low"|"medium"|"high",
  "annotation": "the short label to show on the body, max 6 words",
  "confidence": 0.0-1.0
}}"""
