from langchain_openai import AzureOpenAIEmbeddings
import hashlib
from backend.config import Config
from ..utils.logging_utils import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self):
        try:
            self.client = AzureOpenAIEmbeddings(
                openai_api_version=Config.DIAL_API_VERSION,
                azure_deployment=Config.EMBEDDING_MODEL,
                azure_endpoint=Config.DIAL_ENDPOINT,
                api_key=Config.DIAL_API_KEY,
                check_embedding_ctx_length=False,
            )
            logger.info("Successfully initialized Azure OpenAI Embeddings client")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise

    def embed_documents(self, texts):
        try:
            logger.info(f"Embedding {len(texts)} documents")
            return self.client.embed_documents(texts)
        except Exception as e:
            logger.error(f"Embedding failed: {str(e)}")
            raise

    def embed_query(self, query):
        try:
            logger.info(f"Embedding query: {query[:50]}...")
            return self.client.embed_query(query)
        except Exception as e:
            logger.error(f"Query embedding failed: {str(e)}")
            raise

    @staticmethod
    def calculate_content_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()