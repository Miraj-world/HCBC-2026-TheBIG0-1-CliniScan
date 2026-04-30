from __future__ import annotations

BASE_SEVERITY_WEIGHTS = {
    "open_wound": 5,
    "bleeding": 5,
    "spreading": 4,
    "discharge": 3,
    "swelling": 2,
    "discoloration": 2,
}

CONTEXT_MODIFIERS = {
    "skin": {
        "spreading": 2.0,
        "bleeding": 1.5,
        "discoloration": 1.5,
    },
    "eye": {
        "discharge": 2.5,
        "discoloration": 1.8,
        "spreading": 2.0,
        "swelling": 1.5,
    },
    "respiratory": {
        "swelling": 2.5,
        "spreading": 2.0,
    },
    "musculoskeletal": {
        "swelling": 1.5,
        "bleeding": 1.5,
    },
    "neurological": {
        "spreading": 1.5,
    },
}

CONFIDENCE_MULTIPLIER = {
    "low": 0.6,
    "medium": 0.85,
    "high": 1.0,
}

CONFLICT_MAP = {
    ("low", "high"): "severity_mismatch",
    ("low", "medium"): "minor_discrepancy",
    ("medium", "high"): "underreporting_possible",
}


def calculate_vision_score(severity_indicators: dict, confidence: str, body_region: str) -> float:
    modifiers = CONTEXT_MODIFIERS.get(body_region, {})
    raw_score = 0.0
    for sign, present in severity_indicators.items():
        if present and sign in BASE_SEVERITY_WEIGHTS:
            base_weight = BASE_SEVERITY_WEIGHTS[sign]
            modifier = modifiers.get(sign, 1.0)
            raw_score += base_weight * modifier
    return raw_score * CONFIDENCE_MULTIPLIER.get(confidence, 0.6)


def calculate_text_score(symptom_data: dict) -> float:
    base = float(symptom_data.get("severity_score", 0)) / 2.0
    progression_bonus = 2.0 if symptom_data.get("progression") == "worsening" else 0.0
    risk_factor_bonus = min(len(symptom_data.get("risk_factors", [])), 3) * 1.0
    return base + progression_bonus + risk_factor_bonus


def detect_conflict(symptom_data: dict, vision_data: dict) -> dict:
    text_severity = symptom_data.get("patient_reported_severity", "low")
    vision_severity = vision_data.get("visual_severity", "low")
    conflict_type = CONFLICT_MAP.get((text_severity, vision_severity))
    return {
        "conflict_detected": conflict_type is not None,
        "conflict_type": conflict_type,
        "text_severity": text_severity,
        "vision_severity": vision_severity,
        "visual_dominates": vision_severity == "high" and text_severity == "low",
    }


def compute_urgency(total_score: float, override: dict) -> str:
    if override.get("override_triggered"):
        return "high"
    if total_score >= 8:
        return "high"
    if total_score >= 4:
        return "medium"
    return "low"


def build_risk_signals(symptom_data: dict, vision_data: dict, conflict: dict, override: dict) -> list[str]:
    signals: list[str] = []
    indicators = vision_data.get("severity_indicators", {})

    if indicators.get("spreading"):
        signals.append("Spreading pattern detected visually")
    if indicators.get("open_wound"):
        signals.append("Open wound identified in image")
    if indicators.get("bleeding"):
        signals.append("Signs of bleeding present in image")
    if indicators.get("discharge"):
        signals.append("Discharge observed in image")
    if symptom_data.get("progression") == "worsening":
        signals.append("Patient reports condition is worsening over time")
    if conflict.get("conflict_detected"):
        signals.append("Visual evidence indicates higher severity than patient description suggests")
    if conflict.get("visual_dominates"):
        signals.append("Image analysis was weighted more heavily due to significant severity mismatch")

    for triggered in override.get("triggered_by", []):
        signals.append(f"Critical keyword detected: '{triggered}'")

    return signals


def fuse_evidence(symptom_data: dict, vision_data: dict, override: dict, no_image: bool = False) -> dict:
    body_region = symptom_data.get("body_region", "other")

    if no_image:
        vision_score = 0.0
        text_score = calculate_text_score(symptom_data) * 1.2
        conflict = {
            "conflict_detected": False,
            "conflict_type": None,
            "text_severity": symptom_data.get("patient_reported_severity"),
            "vision_severity": None,
            "visual_dominates": False,
        }
    else:
        vision_score = calculate_vision_score(
            vision_data.get("severity_indicators", {}),
            vision_data.get("confidence", "low"),
            body_region,
        )
        text_score = calculate_text_score(symptom_data)
        conflict = detect_conflict(symptom_data, vision_data)

    total_score = vision_score + text_score
    if conflict.get("conflict_detected"):
        total_score += 2.0

    risk_signals = build_risk_signals(symptom_data, vision_data, conflict, override)

    return {
        "vision_score": round(vision_score, 2),
        "text_score": round(text_score, 2),
        "total_risk_score": round(total_score, 2),
        "urgency": compute_urgency(total_score, override),
        "conflict": conflict,
        "risk_signals": risk_signals,
        "body_region": body_region,
        "no_image_mode": no_image,
    }
