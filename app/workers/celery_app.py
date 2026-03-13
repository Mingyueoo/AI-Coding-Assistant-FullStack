# @Version :1.0
# @Author  : Mingyue
# @File    : celery_app.py
# @Time    : 12/03/2026 20:08
"""
Celery application for async task queue.
Run worker: celery -A app.workers.celery_app worker --loglevel=info
Run beat (if needed): celery -A app.workers.celery_app beat --loglevel=info
"""
from celery import Celery
from app.core.config import config

celery_app = Celery(
    "ai_coding_assistant",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer=config.CELERY_TASK_SERIALIZER,
    accept_content=config.CELERY_ACCEPT_CONTENT,
    result_serializer=config.CELERY_RESULT_SERIALIZER,
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)
