from layers.quality_gate import assess_data_quality


def test_quality_low_when_no_image_and_sparse_text():
    output = assess_data_quality({}, {"text_completeness": 0.2}, no_image=True)

    assert output["quality_level"] == "low"
    assert output["show_uncertain_badge"] is True


def test_quality_penalizes_non_medical_image():
    output = assess_data_quality(
        {"confidence": "high", "medical_relevance": False},
        {"text_completeness": 1.0},
        no_image=False,
    )

    assert output["quality_score"] == 0.6
    assert output["quality_level"] == "medium"
