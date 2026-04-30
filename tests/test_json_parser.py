from layers.json_parser import fallback_diagnosis, normalize_diagnosis_output, parse_json_object


def test_parse_json_object_strips_markdown_fences():
    raw = """```json
{\"possible_conditions\": [\"A\"]}
```"""

    parsed = parse_json_object(raw, fallback={})
    assert parsed["possible_conditions"] == ["A"]


def test_parse_json_object_fallback_on_invalid_json():
    parsed = parse_json_object("not json", fallback={"ok": False})
    assert parsed == {"ok": False}


def test_normalize_diagnosis_confidence_and_disclaimer():
    data = normalize_diagnosis_output(
        {
            "possible_conditions": ["A", "B"],
            "confidence_levels": ["high confidence"],
            "clinical_reasoning": ["one", "two", "three", "four"],
            "recommendation": "Act now",
        }
    )

    assert data["confidence_levels"] == ["High", "Medium"]
    assert len(data["clinical_reasoning"]) == 3
    assert "Not a diagnosis" in data["disclaimer"]


def test_normalize_diagnosis_handles_common_model_variants():
    data = normalize_diagnosis_output(
        {
            "conditions": [
                {"name": "Cellulitis", "confidence": "probable"},
                {"condition": "Contact dermatitis", "confidence": "unlikely"},
            ],
            "clinical_reasoning": (
                "Visual findings suggest higher severity. "
                "The reported symptom pattern is localized. "
                "The mismatch supports prompt review."
            ),
            "red_flags": "Rapid spreading; fever; worsening pain",
            "recommendation": "Seek prompt medical evaluation.",
        }
    )

    assert data["possible_conditions"] == ["Cellulitis", "Contact dermatitis"]
    assert data["confidence_levels"] == ["High", "Low"]
    assert data["clinical_reasoning"] == [
        "Visual findings suggest higher severity.",
        "The reported symptom pattern is localized.",
        "The mismatch supports prompt review.",
    ]
    assert data["red_flags"] == ["Rapid spreading", "fever", "worsening pain"]


def test_fallback_diagnosis_shape():
    data = fallback_diagnosis()
    assert "possible_conditions" in data
    assert "disclaimer" in data
