from __future__ import annotations

import json

from layers.ai_gateway import call_ai
from layers.json_parser import fallback_diagnosis, normalize_diagnosis_output, parse_json_object

SYSTEM_PROMPT = """You are a clinical decision support system.
You receive structured medical evidence and return ONLY a valid JSON object.
No markdown. No explanation. No preamble. No code fences. Raw JSON only."""

USER_PROMPT_TEMPLATE = """Analyze this structured medical evidence and return the JSON response.

Evidence:
{fusion_json}

Data Quality Level: {quality_level}

Return exactly this schema, fully populated:
{{
  "possible_conditions": [],
  "confidence_levels": [],
  "clinical_reasoning": [],
  "red_flags": [],
  "recommendation": "",
  "disclaimer": "Not a diagnosis. Always consult a licensed medical professional."
}}

Rules:
- possible_conditions: 3-5 conditions ranked most to least likely
- confidence_levels: exactly one per condition, exactly "High", "Medium", or "Low"
- clinical_reasoning: exactly 3 plain sentences
- red_flags: critical warning signs only, empty list if none
- recommendation: one sentence starting with an action verb
- If quality_level is low, append to recommendation: (Note: limited input data)
- If urgency is "high", recommendation must be explicitly urgent"""


async def generate_clinical_reasoning(
    fusion_output: dict, quality_output: dict, provider: str, api_key: str
) -> dict:
    user_prompt = USER_PROMPT_TEMPLATE.replace(
        "{fusion_json}", json.dumps(fusion_output, indent=2)
    ).replace(
        "{quality_level}", str(quality_output.get("quality_level", "medium"))
    )

    raw = await call_ai(
        messages=[
            {"role": "user", "content": user_prompt}
        ],
        system_prompt=SYSTEM_PROMPT,
        provider=provider,
        api_key=api_key,
        max_tokens=2000,
    )
    parsed = parse_json_object(raw, fallback=fallback_diagnosis())
    return normalize_diagnosis_output(parsed)
