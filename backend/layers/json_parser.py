from __future__ import annotations

import json
import re
from typing import Any

from models.schemas import STANDARD_DISCLAIMER


def extract_json_object(text: str) -> str:
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end < start:
        return cleaned
    return cleaned[start : end + 1]


def parse_json_object(text: str, fallback: dict[str, Any]) -> dict[str, Any]:
    raw = extract_json_object(text)
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return dict(fallback)
    if not isinstance(value, dict):
        return dict(fallback)
    return value


def normalize_confidence_level(value: Any) -> str:
    if isinstance(value, (float, int)):
        if value > 1:
            value = value / 100
        if value >= 0.67:
            return "High"
        if value <= 0.33:
            return "Low"
        return "Medium"

    text = str(value or "").strip().lower()
    if re.search(r"\b(high|strong|likely|probable)\b", text):
        return "High"
    if re.search(r"\b(low|unlikely|weak|doubtful)\b", text):
        return "Low"
    return "Medium"


def _string_items(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            if isinstance(item, dict):
                text = item.get("condition") or item.get("name") or item.get("title") or item.get("diagnosis")
                if text:
                    items.append(str(text).strip())
            else:
                text = str(item).strip()
                if text:
                    items.append(text)
        return items
    if isinstance(value, str):
        text = value.strip()
        if not text or text.lower() in {"none", "n/a", "not applicable"}:
            return []
        parts = re.split(r"(?:\n+|;\s*|\s*\d+\.\s*)", text)
        return [part.strip(" -") for part in parts if part.strip(" -")]
    return []


def _reasoning_items(value: Any) -> list[str]:
    items = _string_items(value)
    if len(items) == 1:
        sentences = re.split(r"(?<=[.!?])\s+", items[0])
        items = [sentence.strip() for sentence in sentences if sentence.strip()]
    return items[:3]


def normalize_diagnosis_output(data: dict[str, Any]) -> dict[str, Any]:
    out = dict(data)
    raw_conditions = out.get("possible_conditions") or out.get("conditions") or out.get("differential_diagnosis")
    out["possible_conditions"] = _string_items(raw_conditions)

    levels = out.get("confidence_levels") or out.get("confidence") or []
    if not levels and isinstance(raw_conditions, list):
        levels = [
            item.get("confidence") or item.get("confidence_level")
            for item in raw_conditions
            if isinstance(item, dict)
        ]
    if isinstance(levels, dict):
        levels = list(levels.values())
    if not isinstance(levels, list):
        levels = [levels]
    normalized_levels = [normalize_confidence_level(item) for item in levels]
    normalized_levels = normalized_levels[: len(out["possible_conditions"])]
    while len(normalized_levels) < len(out["possible_conditions"]):
        normalized_levels.append("Medium")
    out["confidence_levels"] = normalized_levels

    out["clinical_reasoning"] = _reasoning_items(out.get("clinical_reasoning") or out.get("reasoning"))

    out["red_flags"] = _string_items(out.get("red_flags"))

    out["recommendation"] = str(out.get("recommendation") or "Seek medical evaluation if symptoms persist or worsen.")
    out["disclaimer"] = STANDARD_DISCLAIMER
    return out


def fallback_diagnosis() -> dict[str, Any]:
    return {
        "possible_conditions": [],
        "confidence_levels": [],
        "clinical_reasoning": [
            "Insufficient structured evidence was available to produce a reliable triage summary.",
            "The current result is conservative and should not be used as a diagnosis.",
            "A licensed clinician should review symptoms directly.",
        ],
        "red_flags": ["Clinical reasoning output could not be parsed reliably"],
        "recommendation": "Seek medical evaluation if symptoms persist or worsen.",
        "disclaimer": STANDARD_DISCLAIMER,
    }
