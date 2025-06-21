import pytest
# from .conftest import test_action_agent as agent # Import the agent fixture from conftest.py


def test_recommend_action_hate_high_confidence(test_action_agent):
    """
    Test that recommend_action returns a strong action for high-confidence hate speech.
    """
    classification = {"label": "Hate", "confidence": 0.95}
    reasoning = {}
    result = test_action_agent.recommend_action(classification, reasoning)
    assert result["success"] is True
    assert result["action"].startswith("Remove content")

def test_recommend_action_low_confidence(test_action_agent):
    """
    Test that recommend_action flags for human review if confidence is low.
    """
    classification = {"label": "Toxic", "confidence": 0.5}
    reasoning = {}
    result = test_action_agent.recommend_action(classification, reasoning)
    assert result["action"] == "Flag for human review"
    assert result["severity"] == "Low"