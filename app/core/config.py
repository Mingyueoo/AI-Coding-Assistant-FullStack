# @Version :1.0
# @Author  : Mingyue
# @File    : config.py
# @Time    : 12/03/2026 20:09
"""
Central configuration for the application.
Loads from environment variables with sensible defaults for local development.
"""
import os
from pathlib import Path

# Load .env for local development
_env_path = Path(__file__).resolve().parents[2] / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path)


class Config:
    """Application configuration."""

    # Flask
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key")
    FLASK_ENV: str = os.environ.get("FLASK_ENV", "development")
    DEBUG: bool = os.environ.get("FLASK_DEBUG", "1") == "1"

    # Database
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        "sqlite:///ai_coding_assistant.db"
    )

    # SQLAlchemy (Flask-SQLAlchemy)
    SQLALCHEMY_DATABASE_URI: str = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Redis & Celery
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL") or os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.environ.get("CELERY_RESULT_BACKEND") or os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list = ["json"]
    CELERY_RESULT_SERIALIZER: str = "json"

    # Ollama (if used by tasks)
    OLLAMA_BASE_URL: str = os.environ.get(
        "OLLAMA_BASE_URL",
        "http://localhost:11434/api/generate"
    )
    OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", "llama3.2")


config = Config()
