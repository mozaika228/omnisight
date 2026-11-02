"""Implementation of the MVP video processing job.

The worker intentionally keeps model loading in one module so it can be replaced
by a GPU inference service later without changing API contracts.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import cv2
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sqlalchemy import select

from apps.api.config import settings
from apps.api.database import Job, SessionLocal, Transcript, Video

logger = logging.getLogger(__name__)
COLLECTION = "video_frames"


def _set_job(job_id: str, *, status: str, stage: str, progress: float, error: str | None = None) -> None:
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        if job:
            job.status, job.stage, job.progress, job.error = status, stage, progress, error
            db.commit()


def _transcribe(path: str) -> tuple[str, str | None, list[dict]]:
    """Transcribe with Whisper.  A clear error is recorded if the model is unavailable."""
    import whisper

    model = whisper.load_model(settings.WHISPER_MODEL, device=settings.DEVICE)
    result = model.transcribe(path)
    segments = [
        {"start": item["start"], "end": item["end"], "text": item["text"].strip()}
        for item in result.get("segments", [])
    ]
    return result.get("text", "").strip(), result.get("language"), segments


def _embed_images(frames: list[np.ndarray]) -> np.ndarray:
    from PIL import Image
    import torch
    from transformers import CLIPModel, CLIPProcessor

    model = CLIPModel.from_pretrained(settings.EMBEDDING_MODEL)
    processor = CLIPProcessor.from_pretrained(settings.EMBEDDING_MODEL)
    model.to(settings.DEVICE)
    model.eval()
    images = [Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) for frame in frames]
    inputs = processor(images=images, return_tensors="pt")
    inputs = {key: value.to(settings.DEVICE) for key, value in inputs.items()}
    with torch.no_grad():
        vectors = model.get_image_features(**inputs)
        vectors = vectors / vectors.norm(dim=-1, keepdim=True)
    return vectors.cpu().numpy()


def _extract_frames(path: str, sample_every_seconds: float) -> tuple[float, list[tuple[float, np.ndarray]]]:
    capture = cv2.VideoCapture(path)
    if not capture.isOpened():
        raise ValueError("Could not open uploaded video")
    fps = capture.get(cv2.CAP_PROP_FPS) or 1.0
    frame_count = capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    duration = frame_count / fps
    interval = max(1, int(fps * sample_every_seconds))
    samples: list[tuple[float, np.ndarray]] = []
    index = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if index % interval == 0:
            samples.append((index / fps, frame))
        index += 1
    capture.release()
    if not samples:
        raise ValueError("The video contains no readable frames")
    return duration, samples


def _upsert_embeddings(video_id: str, samples: list[tuple[float, np.ndarray]]) -> None:
    client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
    vectors = _embed_images([frame for _, frame in samples])
    try:
        client.get_collection(COLLECTION)
    except Exception:
        client.create_collection(COLLECTION, vectors_config=VectorParams(size=len(vectors[0]), distance=Distance.COSINE))
    points = [
        PointStruct(
            id=str(uuid5(NAMESPACE_URL, f"omnisight/{video_id}/{index}")),
            vector=vector.tolist(),
            payload={"video_id": video_id, "timestamp_seconds": timestamp},
        )
        for index, ((timestamp, _), vector) in enumerate(zip(samples, vectors))
    ]
    client.upsert(collection_name=COLLECTION, points=points, wait=True)


def process_video(video_id: str, job_id: str) -> None:
    """Run all stages; any exception moves the job and video into `failed`."""
    _set_job(job_id, status="processing", stage="extracting_frames", progress=0.05)
    try:
        with SessionLocal() as db:
            video = db.get(Video, video_id)
            if not video:
                raise ValueError("Video does not exist")
            video.status = "processing"
            path = video.path
            db.commit()
        duration, samples = _extract_frames(path, settings.FRAME_SAMPLE_SECONDS)
        with SessionLocal() as db:
            video = db.get(Video, video_id)
            video.duration_seconds = duration
            db.commit()
        _set_job(job_id, status="processing", stage="transcribing", progress=0.35)
        text, language, segments = _transcribe(path)
        with SessionLocal() as db:
            transcript = db.scalar(select(Transcript).where(Transcript.video_id == video_id))
            if transcript is None:
                transcript = Transcript(video_id=video_id)
                db.add(transcript)
            transcript.text, transcript.language, transcript.segments_json = text, language, json.dumps(segments)
            db.commit()
        _set_job(job_id, status="processing", stage="indexing_embeddings", progress=0.7)
        _upsert_embeddings(video_id, samples)
        with SessionLocal() as db:
            db.get(Video, video_id).status = "completed"
            db.commit()
        _set_job(job_id, status="completed", stage="completed", progress=1.0)
    except Exception as exc:
        logger.exception("Video processing failed for %s", video_id)
        with SessionLocal() as db:
            video = db.get(Video, video_id)
            if video:
                video.status = "failed"
                db.commit()
        _set_job(job_id, status="failed", stage="failed", progress=1.0, error=str(exc))
