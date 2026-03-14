# @Version :1.0
# @Author  : Mingyue
# @File    : tasks.py
# @Time    : 12/03/2026 20:08
"""
Celery tasks for async processing.
Tasks receive record IDs, run in worker, update DB with Flask app context.
"""
import logging
from app.workers.celery_app import celery_app
from app.services import model_service, evaluation_service

logger = logging.getLogger(__name__)


def _with_app_context(fn, *args, **kwargs):
    """Run function inside Flask app context for DB access."""
    from app.app import create_app
    app = create_app()
    with app.app_context():
        return fn(*args, **kwargs)


@celery_app.task(bind=True)
def task_generate_code(self, generation_id: int, prompt_text: str, model_name: str) -> None:
    """
    Async: Generate code and update Generation record in DB.
    Celery runs this; Flask route only enqueues and returns.
    """
    def _do():
        from app.db import db
        from app.models import Generation

        gen = Generation.query.get(generation_id)
        if not gen:
            logger.error(f"task_generate_code: Generation {generation_id} not found")
            return

        try:
            code = model_service.generate_code(prompt_text, model_name)
            gen.generated_code = code
            gen.status = "generated"
        except Exception as e:
            logger.exception(f"task_generate_code failed: {e}")
            gen.status = "failed"
            gen.generated_code = None  # or store error in a separate field if needed
        db.session.commit()
        logger.info(f"task_generate_code done: generation_id={generation_id}, status={gen.status}")

    _with_app_context(_do)


@celery_app.task(bind=True)
def task_evaluate_code(self, evaluation_id: int, code: str) -> None:
    """
    Async: Evaluate code and update Evaluation record in DB.
    Celery runs this; Flask route only enqueues and returns.
    """
    def _do():
        from app.db import db
        from app.models import Evaluation

        ev = Evaluation.query.get(evaluation_id)
        if not ev:
            logger.error(f"task_evaluate_code: Evaluation {evaluation_id} not found")
            return

        try:
            result = evaluation_service.evaluate_code(code)
            ev.result = result["result"]
            ev.error_message = result.get("error_message")
        except Exception as e:
            logger.exception(f"task_evaluate_code failed: {e}")
            ev.result = "failed"
            ev.error_message = str(e)
        db.session.commit()
        logger.info(f"task_evaluate_code done: evaluation_id={evaluation_id}, result={ev.result}")

    _with_app_context(_do)
