#!/usr/bin/env python3
"""
Webpage Classification HTTP API Server

Usage:
    python api_server.py
    python api_server.py --port 8000

Request example:
    curl -X POST http://localhost:8000/classify \
        -H "Content-Type: application/json" \
        -d '{"title": "央行宣布降息", "text": "中国人民银行宣布...", "articleLink": "https://example.com"}'

Response example:
    {
        "top2": [
            {"label": "经济", "score": 0.87},
            {"label": "时政", "score": 0.71}
        ]
    }
"""

import sys
import logging
import argparse
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Max request body size (1MB)
MAX_BODY_SIZE = 1 * 1024 * 1024
# Max text field length (50k chars)
MAX_TEXT_LENGTH = 50000

# Global classifier instance
classifier = None


def load_model(matrix_path: str = None, model_path: str = None):
    """Load embedding model and category matrix."""
    from src.llm.embedding_classifier import QwenEmbeddingClassifier

    if matrix_path is None:
        matrix_path = str(PROJECT_ROOT / "models" / "hard_negative_train6000.pt")
    if model_path is None:
        model_path = str(PROJECT_ROOT / "models" / "Qwen3-VL-Embedding-8B")

    clf = QwenEmbeddingClassifier(model_path=model_path, use_template=False)
    clf.load_category_matrix(matrix_path)
    return clf


# Request/Response models
class ClassifyRequest(BaseModel):
    articleLink: Optional[str] = Field(default="", max_length=2048)
    title: Optional[str] = Field(default="", max_length=MAX_TEXT_LENGTH)
    text: Optional[str] = Field(default="", max_length=MAX_TEXT_LENGTH)


class CategoryScore(BaseModel):
    label: str
    score: float


class ClassifyResponse(BaseModel):
    top2: list[CategoryScore]


# Lifespan: load model on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    global classifier
    logger.info("Loading model...")
    classifier = load_model(
        matrix_path=app.state.matrix_path,
        model_path=app.state.model_path,
    )
    logger.info("Model loaded.")
    yield
    logger.info("Shutting down.")


app = FastAPI(title="Webpage Classifier API", lifespan=lifespan)


@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    """Reject requests with body larger than MAX_BODY_SIZE."""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_BODY_SIZE:
        return JSONResponse(
            status_code=413,
            content={"error": f"Request body too large. Max {MAX_BODY_SIZE} bytes."},
        )
    return await call_next(request)


@app.post("/classify", response_model=ClassifyResponse)
async def classify(req: ClassifyRequest):
    title = req.title or ""
    text = req.text or ""
    article_link = req.articleLink or ""

    if not title and not text:
        raise HTTPException(
            status_code=400,
            detail="At least one of 'title' or 'text' is required.",
        )

    try:
        result = classifier.classify(title=title, url=article_link, content=text)
    except Exception as e:
        logger.error(f"Classification failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Classification failed.")

    sorted_scores = sorted(result.scores.items(), key=lambda x: -x[1])
    top2 = [CategoryScore(label=label, score=round(score, 4)) for label, score in sorted_scores[:2]]

    return ClassifyResponse(top2=top2)


@app.get("/health")
async def health():
    return {"status": "ok"}


def main():
    parser = argparse.ArgumentParser(description="Webpage Classification API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Listen address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Listen port (default: 8000)")
    parser.add_argument("--matrix", help="Category embedding matrix path")
    parser.add_argument("--model", help="Embedding model path")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes (default: 1)")
    args = parser.parse_args()

    app.state.matrix_path = args.matrix
    app.state.model_path = args.model

    logger.info(f"Starting server on {args.host}:{args.port}")
    logger.info(f"  POST /classify  - Classification endpoint")
    logger.info(f"  GET  /health    - Health check")

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        workers=args.workers,
        log_level="info",
    )


if __name__ == "__main__":
    main()
