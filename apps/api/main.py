"""HTTP API for the first usable OmniSight processing flow."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from apps.api.config import settings
from apps.api.database import Job, SessionLocal, Video, init_database, new_id
from services.pipeline.tasks import process_video_task
from services.pipeline.worker import process_video
from services.search.semantic import search as semantic_search

SUPPORTED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm"}
SUPPORTED_SUFFIXES = {".mp4", ".mov", ".webm"}


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title=settings.API_TITLE,
    description="AI-powered video understanding platform",
    version=settings.API_VERSION,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    video_ids: list[str] | None = None
    limit: int = Field(default=10, ge=1, le=100)


def video_payload(video: Video) -> dict:
    return {
        "video_id": video.id,
        "title": video.title,
        "status": video.status,
        "duration_seconds": video.duration_seconds,
        "created_at": video.created_at,
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "omnisight-api", "version": settings.API_VERSION}


@app.get("/api/v1/videos")
async def list_videos():
    with SessionLocal() as db:
        videos = db.query(Video).order_by(Video.created_at.desc()).all()
        return {"videos": [video_payload(video) for video in videos], "total": len(videos)}


@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str):
    with SessionLocal() as db:
        job = db.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return {
            "job_id": job.id,
            "video_id": job.video_id,
            "status": job.status,
            "stage": job.stage,
            "progress": job.progress,
            "error": job.error,
        }


@app.post("/api/v1/videos/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_video(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    title: str | None = Form(default=None),
):
    suffix = Path(video.filename or "").suffix.lower()
    if video.content_type not in SUPPORTED_VIDEO_TYPES and suffix not in SUPPORTED_SUFFIXES:
        raise HTTPException(status_code=415, detail="Only MP4, MOV and WebM files are supported")

    record = Video(id=new_id())
    destination = Path(settings.UPLOAD_DIR) / f"{record.id}{suffix}"
    total = 0
    with destination.open("wb") as output:
        while chunk := await video.read(1024 * 1024):
            total += len(chunk)
            if total > settings.MAX_UPLOAD_BYTES:
                output.close()
                destination.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="Video exceeds the upload size limit")
            output.write(chunk)

    record.title = title or video.filename or "Untitled video"
    record.original_filename = video.filename or "video"
    record.path = str(destination)
    record.content_type = video.content_type
    job = Job(video_id=record.id)
    with SessionLocal() as db:
        db.add_all([record, job])
        db.commit()
        db.refresh(job)

    if settings.TASKS_EAGER:
        background_tasks.add_task(process_video, record.id, job.id)
    else:
        try:
            process_video_task.delay(record.id, job.id)
        except Exception:
            # A local API-only development run remains useful without Redis/Celery.
            background_tasks.add_task(process_video, record.id, job.id)
    return {"video": video_payload(record), "job_id": job.id}


@app.post("/api/v1/search")
async def search_videos(request: SearchRequest):
    try:
        results = semantic_search(request.query, request.video_ids, request.limit)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Search is unavailable: {exc}") from exc
    return {"query": request.query, "results": results, "total": len(results)}
