# @Version :1.0
# @Author  : Mingyue
# @File    : api.py.py
# @Time    : 02/03/2026 19:54
import logging
from flask import Blueprint, request, jsonify
from app.db import db
from app.models import Prompt, Generation, Evaluation
from app.services import model_service, evaluation_service
from app.workers.tasks import task_generate_code, task_evaluate_code

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _error(msg: str, status: int = 400):
    return jsonify({"error": msg}), status


# ── POST /api/prompts ─────────────────────────────────────────────────────────

@api_bp.route("/prompts", methods=["POST"])
def create_prompt():
    data = request.get_json(silent=True) or {}
    prompt_text = (data.get("prompt_text") or "").strip()
    model_name = (data.get("model_name") or "mock-gpt").strip()

    if not prompt_text:
        return _error("prompt_text is required")

    if model_name not in model_service.SUPPORTED_MODELS:
        return _error(f"Unknown model. Supported: {model_service.SUPPORTED_MODELS}")

    # Persist Prompt
    prompt = Prompt(prompt_text=prompt_text, model_name=model_name)
    db.session.add(prompt)
    db.session.flush()

    # Generate code
    generation = Generation(prompt_id=prompt.id, status="pending")
    db.session.add(generation)
    db.session.flush()

    try:
        code = task_generate_code.apply_async(
            args=[prompt_text, model_name],
            queue="celery",
        ).get(timeout=120)
        generation.generated_code = code
        generation.status = "generated"
        db.session.commit()
        logger.info(f"Generated code for prompt_id={prompt.id}")
        return jsonify({
            "prompt_id": prompt.id,
            "generation_id": generation.id,
            "generated_code": code,
            "status": generation.status,
        }), 201
    except Exception as e:
        generation.status = "failed"
        db.session.commit()
        logger.error(f"Generation failed for prompt_id={prompt.id}: {e}")
        return _error(f"Code generation failed: {e}", 500)


# ── GET /api/prompts ──────────────────────────────────────────────────────────

@api_bp.route("/prompts", methods=["GET"])
def list_prompts():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    model_filter = request.args.get("model_name")
    status_filter = request.args.get("status")

    query = Prompt.query.order_by(Prompt.created_at.desc())

    if model_filter:
        query = query.filter(Prompt.model_name == model_filter)

    if status_filter:
        subq = (
            db.session.query(Generation.prompt_id)
            .filter(Generation.status == status_filter)
            .subquery()
        )
        query = query.filter(Prompt.id.in_(subq))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [p.to_dict() for p in pagination.items]

    return jsonify({
        "items": items,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": per_page,
    })


# ── GET /api/prompts/<id> ─────────────────────────────────────────────────────

@api_bp.route("/prompts/<int:prompt_id>", methods=["GET"])
def get_prompt(prompt_id: int):
    prompt = db.session.get(Prompt, prompt_id)
    if not prompt:
        return _error("Prompt not found", 404)
    result = prompt.to_dict()
    result["generations"] = [g.to_dict() for g in prompt.generations]
    return jsonify(result)


# ── POST /api/prompts/<id>/evaluate ──────────────────────────────────────────

@api_bp.route("/prompts/<int:prompt_id>/evaluate", methods=["POST"])
def evaluate_prompt(prompt_id: int):
    prompt = db.session.get(Prompt, prompt_id)
    if not prompt:
        return _error("Prompt not found", 404)

    latest_gen = (
        Generation.query.filter_by(prompt_id=prompt_id, status="generated")
        .order_by(Generation.created_at.desc())
        .first()
    )
    if not latest_gen:
        return _error("No generated code found for this prompt. Generate code first.")

    try:
        eval_result = task_evaluate_code.apply_async(
            args=[latest_gen.generated_code],
            queue="celery",
        ).get(timeout=60)
        evaluation = Evaluation(
            generation_id=latest_gen.id,
            result=eval_result["result"],
            error_message=eval_result["error_message"],
        )
        db.session.add(evaluation)
        db.session.commit()
        logger.info(f"Evaluated generation_id={latest_gen.id}: {eval_result['result']}")
        return jsonify({
            "evaluation_id": evaluation.id,
            "generation_id": latest_gen.id,
            "evaluation_result": eval_result["result"],
            "error_message": eval_result["error_message"],
        })
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        return _error(f"Evaluation failed: {e}", 500)


# ── GET /api/analytics ────────────────────────────────────────────────────────

@api_bp.route("/analytics", methods=["GET"])
def get_analytics():
    from app.services import analytics_service as svc
    try:
        data = svc.get_analytics()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return _error(f"Analytics failed: {e}", 500)