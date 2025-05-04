# Case study | Retrieval of contextual data for RAG 

This project provides a FastAPI-based service to process and retrieve context from a structured dataset using hybrid search via Qdrant.

## Project structure
```
case-study/
├── data/                        # Source and processed data files
├── forward_context/             # Main application code
│   ├── config/                  # Configuration files
│   ├── data_processor/          # Data preparation logic
│   ├── lib/                     # Shared library components
│   ├── utils/                   # Utility scripts
│   ├── vector_database/         # Qdrant ingestion and management
│   ├── hybrid_search.py         # Hybrid search script
│   └── main.py                  # FastAPI entry point
├── qdrant/                      # Qdrant local storage
├── .dvc/                        # DVC tracking for data versioning
├── .venv/                       # Virtual environment (optional)
```

## Getting started
### 1. Clone the Repository
```
git clone https://github.com/your-username/case-study.git
```
```
cd case-study
```
### 2. Install Dependencies
  **Option 1: With Poetry (Recommended)**
  ```
  poetry install
  poetry shell
  ```
  **Option 2: With pip**
  ```
  python -m venv .venv
  source .venv/bin/activate  # or .venv\Scripts\activate on Windows
  pip install -r requirements.txt
  ```
### 3. Start a Qdrant instance with storage mapped to your local ./qdrant_storage directory and ports exposed
```
cd qdrant
```
```
docker run -p 6333:6333 -p 6334:6334 \
  -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
  qdrant/qdrant
```
### 3. Run the API service
```
cd ..
```
**Option 1: Direct Python**
```
python forward_context/main.py
```
**Option 2: With Poetry**
```
poetry run python -m forward_context.main
```
### 4. Access the API
Once running, open your browser at:
[http://localhost:8000/docs](http://localhost:8000/docs)

## Testing
```
poetry run pytest
```

## Functionality
- Cleans HTML content
- Extracts linked sentences from source documents
- Manages vector storage in Qdrant
- Provides hybrid search via a FastAPI interface

## Data & storage
- Input data stored in `/data`
- Qdrant storage directory: `/qdrant/qdrant_storage`
