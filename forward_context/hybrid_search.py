from qdrant_client import models

from forward_context.config.config import QDRANT_COLLECTION_NAME, TOP_K
from forward_context.lib.load_embedding_models import get_embedding_models
from forward_context.utils.get_qdrant_client import get_client


dense_embedding_model, bm25_embedding_model, late_interaction_embedding_model = (
    get_embedding_models()
)


class HybridSearcher:
    def __init__(self, collection_name):
        self.DENSE_MODEL = dense_embedding_model
        self.SPARSE_MODEL = bm25_embedding_model
        self.RERANKING_MODEL = late_interaction_embedding_model
        self.collection_name = collection_name
        self.client = get_client()

    def search(self, text: str):
        dense_vectors = next(self.DENSE_MODEL.query_embed(text))
        sparse_vectors = next(self.SPARSE_MODEL.query_embed(text))
        late_vectors = next(self.RERANKING_MODEL.query_embed(text))

        prefetch = [
            models.Prefetch(
                query=dense_vectors,
                using="all-MiniLM-L6-v2",
                limit=TOP_K * 2,
            ),
            models.Prefetch(
                query=models.SparseVector(**sparse_vectors.as_object()),
                using="bm25",
                limit=TOP_K * 2,
            ),
        ]

        search_results = self.client.query_points(
            QDRANT_COLLECTION_NAME,
            prefetch=prefetch,
            query=late_vectors,
            using="colbertv2.0",
            with_payload=True,
            limit=TOP_K,
        )

        results = []
        for i, hit in enumerate(search_results.points):
            document = hit.payload.get("document", {})
            document["score"] = hit.score
            results.append(document)
        return results
