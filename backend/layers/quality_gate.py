from __future__ import annotations


def assess_data_quality(vision_data: dict, symptom_data: dict, no_image: bool) -> dict:
    vision_conf_score = {"low": 0.4, "medium": 0.75, "high": 1.0}

    if no_image:
        vision_score = 0.4
    else:
        vision_score = vision_conf_score.get(vision_data.get("confidence", "low"), 0.4)

    if not vision_data.get("medical_relevance", True):
        vision_score = 0.2

    text_score = float(symptom_data.get("text_completeness", 0.5))
    text_score = min(max(text_score, 0.0), 1.0)

    quality = (vision_score + text_score) / 2.0

    return {
        "quality_score": round(quality, 2),
        "quality_level": "high" if quality >= 0.75 else "medium" if quality >= 0.5 else "low",
        "show_uncertain_badge": quality < 0.5,
    }
