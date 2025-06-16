import pytest
from backend.agents.action_agent import ActionRecommenderAgent

@pytest.fixture
def agent():
    return ActionRecommenderAgent()

def test_recommend_action_hate_high_confidence(agent):
    classification = {"label": "Hate", "confidence": 0.95}
    reasoning = {}
    result = agent.recommend_action(classification, reasoning)
    assert result["success"] is True
    assert result["action"].startswith("Remove content")

def test_recommend_action_low_confidence(agent):
    classification = {"label": "Toxic", "confidence": 0.5}
    reasoning = {}
    result = agent.recommend_action(classification, reasoning)
    assert result["action"] == "Flag for human review"
    assert result["severity"] == "Low"