import pytest
from unittest.mock import patch, MagicMock
from backend.agents.hate_speech_agent import HateSpeechDetectionAgent

@pytest.fixture
def agent():
    """Fixture to create a HateSpeechDetectionAgent instance for tests."""
    return HateSpeechDetectionAgent()

def test_classify_text_success(agent):
    """
    Test that classify_text returns a successful result with correct label and confidence
    when the LLM call is mocked to return valid JSON.
    """
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"label": "Hate", "confidence": 0.99, "explanation": "Clear hate speech."}'
    with patch.object(agent.client.chat.completions, 'create', return_value=mock_response):
        result = agent.classify_text("Some hateful text")
        assert result["success"] is True
        assert result["label"] == "Hate"
        assert result["confidence"] == 0.99

def test_classify_text_empty_response(agent):
    """
    Test that classify_text returns an error if the LLM response is empty.
    """
    mock_response = MagicMock()
    mock_response.choices = []
    with patch.object(agent.client.chat.completions, 'create', return_value=mock_response):
        result = agent.classify_text("Some text")
        assert result["success"] is False
        assert "Empty response" in result["message"]

def test_classify_text_invalid_json(agent):
    """
    Test that classify_text returns an error if the LLM response is not valid JSON.
    """
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "not a json"
    with patch.object(agent.client.chat.completions, 'create', return_value=mock_response):
        result = agent.classify_text("Some text")
        assert result["success"] is False
        assert "Invalid JSON" in result["message"]