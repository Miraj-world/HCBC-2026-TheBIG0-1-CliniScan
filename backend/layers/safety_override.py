"""Layer 0 safety override."""

from __future__ import annotations

HIGH_RISK_SYMPTOMS = [
    "chest pain",
    "shortness of breath",
    "difficulty breathing",
    "vision loss",
    "sudden confusion",
    "cannot move",
    "severe bleeding",
    "loss of consciousness",
    "stroke",
    "seizure",
    "heart attack",
    "anaphylaxis",
    "allergic reaction",
    "swallowing difficulty",
    "paralysis",
    "unresponsive",
    "overdose",
]


def run_safety_override(raw_text: str) -> dict:
    text_lower = (raw_text or "").lower()
    triggered = [term for term in HIGH_RISK_SYMPTOMS if term in text_lower]
    return {
        "override_triggered": len(triggered) > 0,
        "triggered_by": triggered,
        "forced_urgency": "high" if triggered else None,
    }
