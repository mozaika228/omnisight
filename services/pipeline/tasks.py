"""Celery entry point for extracting, transcribing and indexing a video."""

from celery import Celery

from apps.api.config import settings
from services.pipeline.worker import process_video

celery_app = Celery("omnisight", broker=settings.CELERY_BROKER, backend=settings.CELERY_RESULT_BACKEND)
celery_app.conf.task_track_started = True


@celery_app.task(name="omnisight.process_video", bind=True)
def process_video_task(self, video_id: str, job_id: str) -> None:
    process_video(video_id, job_id)
