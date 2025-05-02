from pathlib import Path

DENSE_EMBEDDING_DIM = 384
RERANKING_EMBEDDING_DIM = 128
BATCH_SIZE = 32

TOP_K = 5
RAW_DATA_FILE = Path(__file__).parent / "../../data/statistics.json"
CLEANED_DESCRIPTION_FILE = (
    Path(__file__).parent / "../../data/statistics_cleaned_descriptions.json"
)
SPLIT_PARAGRAPH_FILE = (
    Path(__file__).parent / "../../data/statistics_split_paragraphs.json"
)
GROUND_TRUTH_FILE = Path(__file__).parent / "../../data/ground_truth.json"

QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION_NAME = "statista-context"
