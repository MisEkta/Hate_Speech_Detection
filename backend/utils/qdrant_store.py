import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from backend.config import Config
from ..utils.logging_utils import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

class QdrantOpenAIStore:
    def __init__(
        self,
        qdrant_host: str = Config.QDRANT_URL,
        qdrant_port: int = Config.QDRANT_PORT,
        collection_name: str = Config.COLLECTION_NAME,
        storage_path: str = "logs/policy_embeddings",
    ):
        self.logger = logger
        self.storage_path = storage_path
        self.collection_name = collection_name
        self.documents = []

        os.makedirs(storage_path, exist_ok=True)
        self.metadata_path = os.path.join(storage_path, "metadata.json")

        try:
            self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
            self.logger.info(f"Successfully connected to Qdrant at {qdrant_host}:{qdrant_port}")
            collections = self.qdrant_client.get_collections()
            self.logger.debug(f"Available collections: {[c.name for c in collections.collections]}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Qdrant: {str(e)}")
            raise

    def _load_metadata(self) -> Dict[str, Any]:
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load metadata: {str(e)}")
        return {}

    def _save_metadata(self, metadata: Dict[str, Any]):
        try:
            with open(self.metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {str(e)}")
            raise

    def _ensure_collection_exists(self):
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]
            if self.collection_name not in collection_names:
                self.logger.info(f"Creating collection: {self.collection_name}")
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI embedding dimension
                        distance=Distance.COSINE,
                    ),
                )
                self.logger.info(f"Collection '{self.collection_name}' created successfully")
            else:
                self.logger.debug(f"Collection '{self.collection_name}' already exists")
        except Exception as e:
            self.logger.error(f"Failed to ensure collection exists: {str(e)}")
            raise

    def upsert_documents(self, points: List[PointStruct]):
        try:
            self.qdrant_client.upsert(
                collection_name=self.collection_name, points=points
            )
            self.logger.info(f"Upserted {len(points)} points to Qdrant")
        except Exception as e:
            self.logger.error(f"Failed to upsert points: {str(e)}")
            raise

    def scroll_documents(self, limit=10000) -> List[Dict[str, Any]]:
        try:
            response = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            documents = []
            for point in response[0]:
                payload = point.payload
                documents.append(
                    {
                        "content": payload["content"],
                        "source": payload["source"],
                        "chunk_id": payload["chunk_id"],
                        "content_hash": payload["content_hash"],
                        "doc_id": payload["doc_id"],
                        "qdrant_id": point.id,
                    }
                )
            self.logger.info(f"Loaded {len(documents)} documents from Qdrant")
            return documents
        except Exception as e:
            self.logger.error(f"Failed to load documents from Qdrant: {str(e)}")
            return []

    def search(self, query_embedding, limit: int = 7) -> List[Dict[str, Any]]:
        try:
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                with_payload=True,
            )
            results = []
            for i, result in enumerate(search_results):
                results.append(
                    {
                        "text": result.payload["content"],
                        "source": result.payload["source"],
                        "chunk_id": result.payload["chunk_id"],
                        "score": round(float(result.score) * 100, 2),
                        "rank": i + 1,
                    }
                )
            self.logger.info(f"Found {len(results)} matching documents")
            return results
        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            raise

    def delete_collection(self):
        try:
            self.qdrant_client.delete_collection(self.collection_name)
            self.logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            self.logger.error(f"Failed to delete collection: {str(e)}")
            raise

    def get_storage_stats(self) -> Optional[Dict[str, Any]]:
        try:
            metadata = self._load_metadata()
            try:
                collection_info = self.qdrant_client.get_collection(
                    self.collection_name
                )
                vector_count = collection_info.points_count
                vector_size = collection_info.config.params.vectors.size
            except:
                vector_count = 0
                vector_size = 0
            stats = {
                "document_count": len(self.documents) if self.documents else 0,
                "embedding_dimension": vector_size,
                "vector_count": vector_count,
                "collection_name": self.collection_name,
                "storage_path": self.storage_path,
                "policy_versions": metadata.get("policy_versions", {}),
                "last_updated": metadata.get("last_updated"),
                "qdrant_connection": {
                    "host": self.qdrant_client._client.host if hasattr(self.qdrant_client, "_client") else "unknown",
                    "port": self.qdrant_client._client.port if hasattr(self.qdrant_client, "_client") else "unknown",
                },
            }
            if os.path.exists(self.metadata_path):
                stats["metadata_size_mb"] = round(
                    os.path.getsize(self.metadata_path) / (1024 * 1024), 2
                )
            else:
                stats["metadata_size_mb"] = 0
            return stats
        except Exception as e:
            self.logger.error(f"Error getting storage stats: {str(e)}")
            return None

    def optimize_index(self):
        try:
            self.logger.info("Triggering Qdrant collection optimization")
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            current_size = collection_info.points_count
            if current_size > 1000:
                self.logger.info(
                    f"Collection has {current_size} points, optimization may improve performance"
                )
                self.logger.info(
                    "Consider configuring HNSW parameters for large collections"
                )
                self.logger.info(
                    "Qdrant automatically handles index optimization in the background"
                )
            else:
                self.logger.info("Collection size doesn't require special optimization")
        except Exception as e:
            self.logger.error(f"Failed to optimize collection: {str(e)}")
            raise

    def health_check(self) -> Dict[str, Any]:
        try:
            collections = self.qdrant_client.get_collections()
            qdrant_healthy = True
            collection_names = [c.name for c in collections.collections]
            collection_exists = self.collection_name in collection_names
            collection_stats = None
            if collection_exists:
                collection_info = self.qdrant_client.get_collection(
                    self.collection_name
                )
                collection_stats = {
                    "points_count": collection_info.points_count,
                    "vector_size": collection_info.config.params.vectors.size,
                    "distance": collection_info.config.params.vectors.distance.value,
                }
            return {
                "qdrant_healthy": qdrant_healthy,
                "collection_exists": collection_exists,
                "collection_stats": collection_stats,
                "local_documents_count": len(self.documents),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "qdrant_healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }