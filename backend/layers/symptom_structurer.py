from __future__ import annotations

from typing import Any

from layers.ai_gateway import call_ai
from layers.json_parser import parse_json_object

STRUCTURER_PROMPT = """You are a medical intake parser.
Convert the patient input below into ONLY a valid JSON object. No markdown. No explanation. No preamble.
Return this exact schema:
{
  \"primary_symptom\": \"\",
  \"body_location\": \"\",
  \"body_region\": \"\",
  \"duration_days\": 0,
  \"severity_score\": 0,
  \"progression\": \"\",
  \"associated_symptoms\": [],
  \"patient_reported_severity\": \"\",
  \"risk_factors\": [],
  \"text_completeness\": 0.0
}
Rules:
- body_region: classify as exactly one of: skin, eye, respiratory, musculoskeletal, gastrointestinal, neurological, other
- severity_score: use the integer provided in form fields (1-10)
- patient_reported_severity: map severity_score. 1-3 = \"low\", 4-6 = \"medium\", 7-10 = \"high\"
- progression: infer from description. Use improving, stable, or worsening
- associated_symptoms: extract secondary symptoms mentioned
- risk_factors: include only explicitly stated risk factors
- text_completeness: float 0.0 to 1.0 for how complete the description is
Patient input:
Symptom description: {symptom_text}
Body location: {body_location}
Duration: {duration_days} days
Severity: {severity_score}/10
Age: {age}
Known conditions: {known_conditions}
Current medications: {medications}"""


DEFAULT_STRUCTURED_OUTPUT = {
    "primary_symptom": "",
    "body_location": "",
    "body_region": "other",
    "duration_days": 0,
    "severity_score": 1,
    "progression": "stable",
    "associated_symptoms": [],
    "patient_reported_severity": "low",
    "risk_factors": [],
    "text_completeness": 0.3,
}


async def structure_symptoms(form_data: dict[str, Any], provider: str, api_key: str) -> dict:
    prompt = STRUCTURER_PROMPT.format(**form_data)
    raw = await call_ai(
        messages=[{"role": "user", "content": prompt}],
        provider=provider,
        api_key=api_key,
        max_tokens=1000,
    )
    return parse_json_object(raw, fallback=DEFAULT_STRUCTURED_OUTPUT)
