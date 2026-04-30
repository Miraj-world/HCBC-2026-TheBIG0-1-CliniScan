from __future__ import annotations

import json

from layers.ai_gateway import call_ai
from layers.json_parser import fallback_diagnosis, normalize_diagnosis_output, parse_json_object

DIAGNOSIS_PROMPT = """You are a clinical decision support system.
You receive structured medical evidence, not raw patient text.
Return ONLY a valid JSON object. No markdown. No explanation outside JSON.
Structured Evidence Input:
{fusion_json}
Data Quality Level: {quality_level}
Return this exact schema:
{
  \"possible_conditions\": [],
  \"confidence_levels\": [],
  \"clinical_reasoning\": [],
  \"red_flags\": [],
  \"recommendation\": \"\",
  \"disclaimer\": \"Not a diagnosis. Always consult a licensed medical professional.\"
}
Rules:
- possible_conditions: list 3-5 conditions, ranked most to least likely
- confidence_levels: one entry per condition, exactly High, Medium, or Low
- clinical_reasoning: exactly 3 sentences
- red_flags: include only critical warning signs
- recommendation: one plain-English sentence. Start with an action verb
- If data quality is low, append: (Note: limited input data - results have reduced confidence)
- If urgency in input is high due to safety override, recommendation must be explicitly urgent"""


async def generate_clinical_reasoning(fusion_output: dict, quality_output: dict, provider: str, api_key: str) -> dict:
    prompt = DIAGNOSIS_PROMPT.format(
        fusion_json=json.dumps(fusion_output, indent=2),
        quality_level=quality_output.get("quality_level", "medium"),
    )

    raw = await call_ai(
        messages=[{"role": "user", "content": prompt}],
        provider=provider,
        api_key=api_key,
        max_tokens=1000,
    )
    parsed = parse_json_object(raw, fallback=fallback_diagnosis())
    return normalize_diagnosis_output(parsed)
