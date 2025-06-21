import pytest
from unittest.mock import patch, MagicMock
# from .conftest import test_hatespeech_agent as agent  # Import the agent fixture from conftest.py


def test_classify_text_success(test_hatespeech_agent):
    """
    Test that classify_text returns a successful result with correct label and confidence
    when the LLM call is mocked to return valid JSON.
    """
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"label": "Hate", "confidence": 0.99, "explanation": "Clear hate speech."}'
    with patch.object(test_hatespeech_agent.client.chat.completions, 'create', return_value=mock_response):
        result = test_hatespeech_agent.classify_text("Some hateful text")
        assert result["success"] is True
        assert result["label"] == "Hate"
        assert result["confidence"] == 0.99

def test_classify_text_empty_response(test_hatespeech_agent):
    """
    Test that classify_text returns an error if the LLM response is empty.
    """
    mock_response = MagicMock()
    mock_response.choices = []
    with patch.object(test_hatespeech_agent.client.chat.completions, 'create', return_value=mock_response):
        result = test_hatespeech_agent.classify_text("Some text")
        assert result["success"] is False
        assert "Empty response" in result["message"]

def test_classify_text_invalid_json(test_hatespeech_agent):
    """
    Test that classify_text returns an error if the LLM response is not valid JSON.
    """
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "not a json"
    with patch.object(test_hatespeech_agent.client.chat.completions, 'create', return_value=mock_response):
        result = test_hatespeech_agent.classify_text("Some text")
        assert result["success"] is False
        assert "Invalid JSON" in result["message"]