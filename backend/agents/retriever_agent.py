from ..utils.embedding_utils import EmbeddingGenerator
from ..utils.qdrant_store import QdrantOpenAIStore
from openai import AzureOpenAI
from typing import List, Dict
from backend.config import Config
from ..agents.error_handler import ErrorHandler
from ..utils.logging_utils import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

class HybridRetrieverAgent:
    def __init__(self):
        self.Qdrant_store = QdrantOpenAIStore()
        self.embedding_generator = EmbeddingGenerator()
        self.Qdrant_store._ensure_collection_exists()
        self.client = AzureOpenAI(
            api_key=Config.DIAL_API_KEY,
            api_version=Config.DIAL_API_VERSION,
            azure_endpoint=Config.DIAL_ENDPOINT
        )
        self.error_handler = ErrorHandler()

    def retrieve_policies(self, text: str, classification: str) -> Dict:
        """Retrieve relevant policy documents using hybrid approach"""
        try:
            # Vector search
            query_embedding = self.embedding_generator.embed_query(text)
            vector_results = self.Qdrant_store.search(query_embedding, limit=7)

            # LLM-enhanced query expansion
            expanded_query = self._expand_query(text, classification)
            expanded_embedding = self.embedding_generator.embed_query(expanded_query)
            llm_results = self.Qdrant_store.search(expanded_embedding, limit=6)

            # Combine and deduplicate results
            all_results = vector_results + llm_results
            unique_results = self._deduplicate_results(all_results)

            return {
                "success": True,
                "documents": unique_results[:5],  # Top 5 results
                "total_found": len(unique_results)
            }

        except Exception as e:
            return self.error_handler.handle_error(e, "HybridRetrieverAgent.retrieve_policies")

    def _expand_query(self, text: str, classification: str) -> str:
        """Use LLM to expand query for better retrieval"""
        try:
            prompt = f"""
            Given this text classified as "{classification}", generate keywords and phrases 
            that would help find relevant policy documents:

            Text: "{text}"
            Classification: {classification}

            Return only the expanded search terms, separated by spaces.
            """

            response = self.client.chat.completions.create(
                model=Config.DEPLOYMENT_NAME,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return text  # Fallback to original text

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on text content"""
        seen_texts = set()
        unique_results = []

        for result in results:
            text_key = result["text"][:100]  # Use first 100 chars as key
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_results.append(result)

        return unique_results