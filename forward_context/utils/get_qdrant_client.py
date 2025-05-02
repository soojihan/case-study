from qdrant_client import QdrantClient
from forward_context.config.config import QDRANT_URL, QDRANT_COLLECTION_NAME
from forward_context.utils.configure_logger import configure_logging

logging = configure_logging()


def get_client():
    """
    Import the Qdrant client
    """
    client = QdrantClient(url=QDRANT_URL)
    return client


def get_collection_info():
    collection_info = client.get_collection(collection_name=QDRANT_COLLECTION_NAME)
    print(collection_info)


def count_documents():
    """
    Count the total number of documents in the index
    """
    count_result = client.count(collection_name=QDRANT_COLLECTION_NAME, exact=True)
    logging("Number of documents:", count_result.count)


if __name__ == "__main__":
    client = get_client()
    get_collection_info()
    count_documents()
