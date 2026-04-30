from __future__ import annotations

from layers.ai_gateway import call_ai
from layers.json_parser import parse_json_object

VISION_PROMPT = """You are a clinical image analysis assistant.
Analyze this medical image and return ONLY a valid JSON object. No markdown. No explanation text. No preamble.
First: Is this image medically relevant? (skin condition, wound, eye, rash, burn, bruise, swelling, or similar)
If NOT medically relevant, return exactly: {\"medical_relevance\": false}
If medically relevant, return this exact schema with all fields filled:
{
  \"medical_relevance\": true,
  \"visual_features\": {
    \"primary_color\": \"\",
    \"texture\": \"\",
    \"shape\": \"\",
    \"spread_pattern\": \"\",
    \"border_definition\": \"\"
  },
  \"severity_indicators\": {
    \"open_wound\": false,
    \"bleeding\": false,
    \"swelling\": false,
    \"spreading\": false,
    \"discoloration\": false,
    \"discharge\": false
  },
  \"visual_severity\": \"\",
  \"confidence\": \"\",
  \"detected_signs\": []
}
Rules:
- visual_severity: must be exactly \"low\", \"medium\", or \"high\"
- confidence: must be exactly \"low\", \"medium\", or \"high\"
- border_definition: must be exactly \"defined\", \"diffuse\", or \"irregular\"
- detected_signs: 2-4 plain English clinical observations only, never a diagnosis
- Never include diagnosis, condition name, or medical conclusion in your response."""


def fallback_vision_output() -> dict:
    return {
        "medical_relevance": True,
        "visual_features": {},
        "severity_indicators": {
            "open_wound": False,
            "bleeding": False,
            "swelling": False,
            "spreading": False,
            "discoloration": False,
            "discharge": False,
        },
        "visual_severity": "low",
        "confidence": "low",
        "detected_signs": [],
    }


async def extract_vision_features(image_base64: str, media_type: str, provider: str, api_key: str) -> dict:
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_base64,
                    },
                },
                {"type": "text", "text": VISION_PROMPT},
            ],
        }
    ]

    raw = await call_ai(messages=messages, provider=provider, api_key=api_key, max_tokens=1000)
    return parse_json_object(raw, fallback=fallback_vision_output())
