from fastapi import FastAPI
from fastapi_camelcase import CamelModel
from pydantic import Field
from typing import List
from forward_context.hybrid_search import HybridSearcher
from forward_context.config.config import QDRANT_COLLECTION_NAME
from forward_context.lib.evaluation import get_eval_metrics
from forward_context.utils.configure_logger import configure_logging
from forward_context.lib.load_data import load_ground_gruth


logger = configure_logging()
app = FastAPI(
    title="Forward Context API",
    description="API for retrieving relevant context based on user queries",
    version="1.0.0",
)

hybrid_searcher = HybridSearcher(collection_name=QDRANT_COLLECTION_NAME)
ground_truth = load_ground_gruth()


class ForwardContextRequest(CamelModel):
    query: str = Field(..., description="Input query used to retrieve relevant context")


class DocumentPayload(CamelModel):
    id: int
    title: str
    subject: str
    link: str
    date: str
    teaser_image_url: str
    paragraph_id: str
    paragraph_clean_text: str
    score: float


class ForwardContextResponse(CamelModel):
    result: List[DocumentPayload] = Field(
        ..., description="Top-5 most relevant documents with scores"
    )


@app.post("/forward-context", response_model=ForwardContextResponse)
def forward_context(request: ForwardContextRequest):
    """
    Retrieve relevant context based on the input query.
    Returns top matching documents and logs evaluation metrics if ground truth exists.
    """
    results = hybrid_searcher.search(text=request.query)

    eval_metrics = None

    if request.query in ground_truth:
        result_ids = [(str(result["id"]), result["score"]) for result in results]
        eval_metrics = get_eval_metrics(result_ids, ground_truth[request.query])

        logger.info(
            "query=%s | top=%s | eval=%s",
            request.query.replace("\n", " "),
            list(set(result_ids)),
            eval_metrics,
        )

    return ForwardContextResponse(result=results)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
