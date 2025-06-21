import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pytest
from backend.agents.action_agent import ActionRecommenderAgent
from backend.agents.hate_speech_agent import HateSpeechDetectionAgent
from backend.agents.retriever_agent import HybridRetrieverAgent
from backend.agents.reasoning_agent import PolicyReasoningAgent
from backend.agents.action_agent import ActionRecommenderAgent


@pytest.fixture
def test_action_agent():
    """Fixture to create an ActionRecommenderAgent instance for tests."""
    return ActionRecommenderAgent()


@pytest.fixture
def test_hatespeech_agent():
    """Fixture to create a HateSpeechDetectionAgent instance for tests."""
    return HateSpeechDetectionAgent()

@pytest.fixture
def test_policy_agent():
    """Fixture to create a PolicyReasoningAgent instance for tests."""
    return PolicyReasoningAgent()


@pytest.fixture
def test_retriever_agent():
    """Fixture to create a HybridRetrieverAgent instance for tests."""
    return HybridRetrieverAgent()