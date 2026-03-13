# @Version :1.0
# @Author  : Mingyue
# @File    : tasks.py
# @Time    : 12/03/2026 20:08
"""
Celery tasks for async processing.
Wraps model_service.generate_code and evaluation_service.evaluate_code.
"""
import logging
from app.workers.celery_app import celery_app
from app.services import model_service, evaluation_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def task_generate_code(self, prompt_text: str, model_name: str) -> str:
    """
    Async task: Generate code via model_service.generate_code().
    Used by API and web routes.
    """
    logger.info(f"Task task_generate_code: model={model_name}, prompt_len={len(prompt_text)}")
    try:
        code = model_service.generate_code(prompt_text, model_name)
        logger.info(f"Task task_generate_code completed: {len(code)} chars")
        return code
    except Exception as e:
        logger.exception(f"Task task_generate_code failed: {e}")
        raise


@celery_app.task(bind=True)
def task_evaluate_code(self, code: str) -> dict:
    """
    Async task: Evaluate code via evaluation_service.evaluate_code().
    Returns: {result: str, error_message: str|None}
    """
    logger.info("Task task_evaluate_code started")
    try:
        result = evaluation_service.evaluate_code(code)
        logger.info(f"Task task_evaluate_code completed: {result['result']}")
        return result
    except Exception as e:
        logger.exception(f"Task task_evaluate_code failed: {e}")
        raise
