# @Version :1.0
# @Author  : Mingyue
# @File    : web.py.py
# @Time    : 02/03/2026 19:56
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db import db
from app.models import Prompt, Generation
from app.services import model_service
from app.workers.tasks import task_generate_code, task_evaluate_code

logger = logging.getLogger(__name__)

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def index():
    return render_template("index.html", models=model_service.SUPPORTED_MODELS)


@web_bp.route("/generate", methods=["POST"])
def generate():
    prompt_text = (request.form.get("prompt_text") or "").strip()
    model_name = (request.form.get("model_name") or "mock-gpt").strip()

    if not prompt_text:
        flash("Please enter a prompt.", "warning")
        return redirect(url_for("web.index"))

    from app.routes.api import create_prompt
    from flask import current_app
    with current_app.test_request_context(
        "/api/prompts",
        method="POST",
        json={"prompt_text": prompt_text, "model_name": model_name},
    ):
        # Use the service layer directly instead
        pass

    # Direct service call
    prompt = Prompt(prompt_text=prompt_text, model_name=model_name)
    db.session.add(prompt)
    db.session.flush()

    generation = Generation(prompt_id=prompt.id, status="pending")
    db.session.add(generation)
    db.session.flush()

    error = None
    try:
        code = task_generate_code.apply_async(
            args=[prompt_text, model_name],
            queue="celery",
        ).get(timeout=120)
        generation.generated_code = code
        generation.status = "generated"
    except Exception as e:
        generation.status = "failed"
        error = str(e)
        logger.error(f"Web generation failed: {e}")
    finally:
        db.session.commit()

    return render_template(
        "result.html",
        prompt=prompt,
        generation=generation,
        error=error,
    )


@web_bp.route("/history")
def history():
    page = request.args.get("page", 1, type=int)
    model_filter = request.args.get("model_name", "")
    status_filter = request.args.get("status", "")

    query = Prompt.query.order_by(Prompt.created_at.desc())
    if model_filter:
        query = query.filter(Prompt.model_name == model_filter)
    if status_filter:
        from sqlalchemy import exists
        query = query.filter(
            exists().where(
                Generation.prompt_id == Prompt.id,
                Generation.status == status_filter,
            )
        )

    pagination = query.paginate(page=page, per_page=15, error_out=False)

    return render_template(
        "history.html",
        prompts=pagination.items,
        pagination=pagination,
        models=model_service.SUPPORTED_MODELS,
        selected_model=model_filter,
        selected_status=status_filter,
    )


@web_bp.route("/dashboard")
def dashboard():
    from app.services import analytics_service
    try:
        analytics = analytics_service.get_analytics()
    except Exception as e:
        logger.error(f"Dashboard analytics error: {e}")
        analytics = {}
    return render_template("dashboard.html", analytics=analytics)


@web_bp.route("/evaluate/<int:prompt_id>", methods=["POST"])
def evaluate(prompt_id: int):
    from app.services import evaluation_service
    prompt = db.session.get(Prompt, prompt_id)
    if not prompt:
        flash("Prompt not found.", "danger")
        return redirect(url_for("web.history"))

    latest_gen = (
        Generation.query.filter_by(prompt_id=prompt_id, status="generated")
        .order_by(Generation.created_at.desc())
        .first()
    )
    if not latest_gen:
        flash("No generated code to evaluate.", "warning")
        return redirect(url_for("web.history"))

    from app.models import Evaluation
    eval_result = task_evaluate_code.apply_async(
        args=[latest_gen.generated_code],
        queue="celery",
    ).get(timeout=60)
    ev = Evaluation(
        generation_id=latest_gen.id,
        result=eval_result["result"],
        error_message=eval_result["error_message"],
    )
    db.session.add(ev)
    db.session.commit()
    flash(f"Evaluation complete: {eval_result['result'].replace('_', ' ').title()}", "success")
    return redirect(url_for("web.history"))