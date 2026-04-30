from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def test_health_endpoint_reports_provider_config_state():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "providers" in body


def test_demo_scenario_uses_cached_response_without_keys():
    response = client.post(
        "/analyze",
        json={
            "symptom_text": "This is demo text input",
            "body_location": "demo",
            "duration_days": 1,
            "severity_score": 3,
            "provider": "anthropic",
            "demo_scenario": 1,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["demo_mode"] is True
    assert "pipeline_stages" in body


def test_missing_provider_key_returns_400(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post(
        "/analyze",
        json={
            "symptom_text": "My symptom text is long enough",
            "body_location": "arm",
            "duration_days": 1,
            "severity_score": 4,
            "provider": "openai",
        },
    )

    assert response.status_code == 400
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_text_only_analysis_path_with_mocked_layers(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    async def fake_structure(form_data, provider, api_key):
        return {
            "primary_symptom": "itch",
            "body_location": form_data["body_location"],
            "body_region": "skin",
            "duration_days": form_data["duration_days"],
            "severity_score": form_data["severity_score"],
            "progression": "stable",
            "associated_symptoms": [],
            "patient_reported_severity": "medium",
            "risk_factors": [],
            "text_completeness": 0.9,
        }

    async def fake_reasoning(fusion_output, quality_output, provider, api_key):
        return {
            "possible_conditions": ["Dermatitis"],
            "confidence_levels": ["Medium"],
            "clinical_reasoning": ["a", "b", "c"],
            "red_flags": [],
            "recommendation": "Monitor symptoms.",
            "disclaimer": "Not a diagnosis. Always consult a licensed medical professional.",
        }

    monkeypatch.setattr(main, "structure_symptoms", fake_structure)
    monkeypatch.setattr(main, "generate_clinical_reasoning", fake_reasoning)

    response = client.post(
        "/analyze",
        json={
            "symptom_text": "My symptom text is long enough",
            "body_location": "arm",
            "duration_days": 2,
            "severity_score": 5,
            "provider": "anthropic",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["no_image_mode"] is True
    assert body["demo_mode"] is False
    assert body["pipeline_stages"]["vision_output"] == {}
