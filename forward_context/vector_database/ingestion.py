from qdrant_client.models import PointStruct
from forward_context.lib.load_data import load_data
from forward_context.lib.load_embedding_models import get_embedding_models

from forward_context.utils.get_qdrant_client import get_client
from forward_context.utils.configure_logger import configure_logging

from forward_context.config.config import (
    SPLIT_PARAGRAPH_FILE,
    QDRANT_COLLECTION_NAME,
    BATCH_SIZE,
)

from tqdm import tqdm
import joblib


logging = configure_logging()

client = get_client()
data = load_data(SPLIT_PARAGRAPH_FILE)

dense_embedding_model, bm25_embedding_model, late_interaction_embedding_model = (
    get_embedding_models()
)


def generate_embeddings():
    """
    Generate document embeddings using three different models.

    Each input document is a string combining title, subject, and paragraph text.
    Embeddings are computed in batches and returned as three separate lists.
    """
    documents = [
        f"Title: {obj['title']}\nSubject: {obj['subject']}\nText: {obj['paragraph_clean_text']}"
        for obj in data
    ]
    dense_embeddings = list(
        dense_embedding_model.embed(documents, batch_size=BATCH_SIZE)
    )
    bm25_embeddings = list(bm25_embedding_model.embed(documents, batch_size=BATCH_SIZE))
    late_interaction_embeddings = list(
        late_interaction_embedding_model.embed(documents, batch_size=BATCH_SIZE)
    )

    return dense_embeddings, bm25_embeddings, late_interaction_embeddings


def batch(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def ingestion():
    dense_embeddings, bm25_embeddings, late_interaction_embeddings = (
        generate_embeddings()
    )
    logging.info("Completed embedding generation")
    points = []
    for dense_embedding, bm25_embedding, late_interaction_embedding, doc in tqdm(
        zip(dense_embeddings, bm25_embeddings, late_interaction_embeddings, data)
    ):
        paragraph_id = doc["paragraph_id"]
        del doc["paragraph_raw_text"]
        point = PointStruct(
            id=paragraph_id,
            vector={
                "all-MiniLM-L6-v2": dense_embedding,
                "bm25": bm25_embedding.as_object(),
                "colbertv2.0": late_interaction_embedding,
            },
            payload={"document": doc},
        )
        points.append(point)

    for batch_points in tqdm(batch(points, BATCH_SIZE), desc="Uploading to Qdrant"):
        operation_info = client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=batch_points,
        )
        logging.info(operation_info)


if __name__ == "__main__":
    ingestion()
