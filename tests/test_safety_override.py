from layers.safety_override import run_safety_override


def test_safety_override_triggers_high_urgency_keyword():
    output = run_safety_override("I suddenly have chest pain and shortness of breath")

    assert output["override_triggered"] is True
    assert output["forced_urgency"] == "high"
    assert "chest pain" in output["triggered_by"]


def test_safety_override_no_trigger():
    output = run_safety_override("Mild itch on my arm for two days")

    assert output == {
        "override_triggered": False,
        "triggered_by": [],
        "forced_urgency": None,
    }
