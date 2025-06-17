import pytest
from unittest.mock import patch, MagicMock
from backend.agents.retriever_agent import HybridRetrieverAgent

@pytest.fixture
def agent():
    """Fixture to create a HybridRetrieverAgent instance for tests."""
    return HybridRetrieverAgent()

def test_retrieve_policies_success(agent):
    """
    Test that retrieve_policies returns a successful result and correct document structure
    when embedding and search methods are mocked.
    """
    with patch.object(agent.embedding_generator, 'embed_query', return_value=[0.1, 0.2]), \
         patch.object(agent.Qdrant_store, 'search', return_value=[{"text": "Policy1"}, {"text": "Policy2"}]), \
         patch.object(agent, '_expand_query', return_value="expanded query"):
        result = agent.retrieve_policies("test", "Hate")
        assert result["success"] is True
        assert isinstance(result["documents"], list)
        assert result["total_found"] == len(result["documents"])

def test_expand_query_fallback(agent):
    """
    Test that _expand_query falls back to the original text if the LLM call fails.
    """
    with patch.object(agent.client.chat.completions, 'create', side_effect=Exception("fail")):
        expanded = agent._expand_query("text", "Hate")
        assert expanded == "text"

def test_deduplicate_results(agent):
    """
    Test that _deduplicate_results removes duplicate entries based on text content.
    """
    results = [{"text": "abc"}, {"text": "abc"}, {"text": "def"}]
    unique = agent._deduplicate_results(results)
    assert len(unique) == 2