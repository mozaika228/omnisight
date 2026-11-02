"""Qdrant-backed semantic search for indexed video frames."""

from __future__ import annotations

from qdrant_client import QdrantClient

from apps.api.config import settings
from services.pipeline.worker import COLLECTION


def _embed_query(query: str) -> list[float]:
    import torch
    from transformers import CLIPModel, CLIPProcessor

    model = CLIPModel.from_pretrained(settings.EMBEDDING_MODEL)
    processor = CLIPProcessor.from_pretrained(settings.EMBEDDING_MODEL)
    model.to(settings.DEVICE)
    model.eval()
    inputs = processor(text=[query], return_tensors="pt", padding=True)
    inputs = {key: value.to(settings.DEVICE) for key, value in inputs.items()}
    with torch.no_grad():
        vector = model.get_text_features(**inputs)
        vector = vector / vector.norm(dim=-1, keepdim=True)
    return vector[0].cpu().tolist()


def search(query: str, video_ids: list[str] | None, limit: int) -> list[dict]:
    client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
    query_filter = None
    if video_ids:
        from qdrant_client.models import FieldCondition, Filter, MatchAny

        query_filter = Filter(must=[FieldCondition(key="video_id", match=MatchAny(any=video_ids))])
    hits = client.search(
        collection_name=COLLECTION,
        query_vector=_embed_query(query),
        query_filter=query_filter,
        limit=limit,
    )
    return [{"video_id": hit.payload["video_id"], "timestamp_seconds": hit.payload["timestamp_seconds"], "confidence": hit.score} for hit in hits]
