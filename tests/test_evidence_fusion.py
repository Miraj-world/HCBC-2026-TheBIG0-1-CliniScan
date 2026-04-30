from layers.evidence_fusion import calculate_vision_score, fuse_evidence


def test_confidence_dampens_vision_score():
    indicators = {"discharge": True}

    low = calculate_vision_score(indicators, "low", "eye")
    high = calculate_vision_score(indicators, "high", "eye")

    assert low < high


def test_no_image_mode_compensation_and_no_conflict():
    symptom = {
        "body_region": "skin",
        "severity_score": 5,
        "progression": "stable",
        "risk_factors": [],
        "patient_reported_severity": "medium",
    }

    output = fuse_evidence(symptom, {}, {"override_triggered": False, "triggered_by": []}, no_image=True)

    assert output["vision_score"] == 0.0
    assert output["no_image_mode"] is True
    assert output["conflict"]["conflict_detected"] is False


def test_conflict_adds_risk_bonus():
    symptom = {
        "body_region": "eye",
        "severity_score": 4,
        "progression": "stable",
        "risk_factors": [],
        "patient_reported_severity": "low",
    }
    vision = {
        "severity_indicators": {"discharge": True},
        "confidence": "high",
        "visual_severity": "high",
    }

    output = fuse_evidence(symptom, vision, {"override_triggered": False, "triggered_by": []}, no_image=False)

    assert output["conflict"]["conflict_detected"] is True
    assert output["conflict"]["conflict_type"] == "severity_mismatch"
    assert output["total_risk_score"] > output["vision_score"] + output["text_score"] - 0.01
