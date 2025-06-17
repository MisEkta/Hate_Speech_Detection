import pytest
from unittest.mock import patch, MagicMock
from backend.agents.reasoning_agent import PolicyReasoningAgent

@pytest.fixture
def agent():
    """Fixture to create a PolicyReasoningAgent instance for tests."""
    return PolicyReasoningAgent()

def test_generate_reasoning_success(agent):
    """
    Test that generate_reasoning returns a successful result and includes reasoning text
    when the LLM call is mocked.
    """
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Reasoning text"
    with patch.object(agent.client.chat.completions, 'create', return_value=mock_response):
        result = agent.generate_reasoning("text", {"label": "Hate", "confidence": 0.9, "explanation": "exp"}, [{"source": "src", "text": "policy"}])
        assert result["success"] is True
        assert "reasoning" in result

def test_prepare_context(agent):
    """
    Test that _prepare_context correctly formats context from a list of policy documents.
    """
    docs = [{"source": "A", "text": "T1"}, {"source": "B", "text": "T2"}]
    context = agent._prepare_context(docs)
    assert "From A" in context and "From B" in context