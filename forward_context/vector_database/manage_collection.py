# source: https://qdrant.tech/documentation/search-precision/reranking-hybrid-search/
from qdrant_client.models import models
from forward_context.utils.get_qdrant_client import get_client
from forward_context.config.config import (
    DENSE_EMBEDDING_DIM,
    QDRANT_COLLECTION_NAME,
    RERANKING_EMBEDDING_DIM,
)
from forward_context.utils.configure_logger import configure_logging

logging = configure_logging()

client = get_client()


def create_collection(collection_name: str):
    if client.collection_exists(collection_name=collection_name):
        logging.info("collection already exists")
    else:
        client.create_collection(
            collection_name,
            vectors_config={
                "all-MiniLM-L6-v2": models.VectorParams(
                    size=DENSE_EMBEDDING_DIM,
                    distance=models.Distance.COSINE,
                ),
                "colbertv2.0": models.VectorParams(
                    size=RERANKING_EMBEDDING_DIM,
                    distance=models.Distance.COSINE,
                    multivector_config=models.MultiVectorConfig(
                        comparator=models.MultiVectorComparator.MAX_SIM,
                    ),
                ),
            },
            sparse_vectors_config={
                "bm25": models.SparseVectorParams(modifier=models.Modifier.IDF)
            },
        )
        logging.info(f"collection {QDRANT_COLLECTION_NAME} created")


def delete_client(collection_name):
    client.delete_collection(collection_name=collection_name)


if __name__ == "__main__":
    create_collection(QDRANT_COLLECTION_NAME)
    # delete_client(QDRANT_COLLECTION_NAME)
