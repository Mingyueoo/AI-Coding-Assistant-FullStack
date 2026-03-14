# @Version :1.0
# @Author  : Mingyue
# @File    : web.py
# @Time    : 02/03/2026 19:56
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db import db
from app.models import Prompt, Generation, Evaluation
from app.services import model_service
from app.workers.tasks import task_generate_code, task_evaluate_code

logger = logging.getLogger(__name__)

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def index():
    return render_template("index.html", models=model_service.SUPPORTED_MODELS)


@web_bp.route("/generate", methods=["POST"])
def generate():
    """Create records, enqueue task, redirect to wait page immediately."""
    prompt_text = (request.form.get("prompt_text") or "").strip()
    model_name = (request.form.get("model_name") or "mock-gpt").strip()

    if not prompt_text:
        flash("Please enter a prompt.", "warning")
        return redirect(url_for("web.index"))

    prompt = Prompt(prompt_text=prompt_text, model_name=model_name)
    db.session.add(prompt)
    db.session.flush()

    generation = Generation(prompt_id=prompt.id, status="pending")
    db.session.add(generation)
    db.session.flush()

    task_generate_code.delay(generation.id, prompt_text, model_name)
    db.session.commit()

    return redirect(url_for("web.generate_wait", generation_id=generation.id))


@web_bp.route("/generate/wait/<int:generation_id>")
def generate_wait(generation_id: int):
    """Wait page: polls API until status is generated or failed."""
    gen = db.session.get(Generation, generation_id)
    if not gen:
        flash("Generation not found.", "danger")
        return redirect(url_for("web.index"))
    return render_template("generate_wait.html", generation=gen)


@web_bp.route("/generate/result/<int:generation_id>")
def generate_result(generation_id: int):
    """Show result after generation completes."""
    generation = db.session.get(Generation, generation_id)
    if not generation:
        flash("Generation not found.", "danger")
        return redirect(url_for("web.index"))
    prompt = db.session.get(Prompt, generation.prompt_id)
    return render_template(
        "result.html",
        prompt=prompt,
        generation=generation,
        error=None if generation.status == "generated" else "Code generation failed",
    )


@web_bp.route("/history")
def history():
    page = request.args.get("page", 1, type=int)
    model_filter = request.form.get("model_name") or request.args.get("model_name", "")
    status_filter = request.form.get("status") or request.args.get("status", "")

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
    """Create evaluation (pending), enqueue task, redirect to wait page."""
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

    evaluation = Evaluation(
        generation_id=latest_gen.id,
        result="pending",
        error_message=None,
    )
    db.session.add(evaluation)
    db.session.flush()

    task_evaluate_code.delay(evaluation.id, latest_gen.generated_code)
    db.session.commit()

    return redirect(url_for("web.evaluate_wait", evaluation_id=evaluation.id))


@web_bp.route("/evaluate/wait/<int:evaluation_id>")
def evaluate_wait(evaluation_id: int):
    """Wait page: polls API until evaluation completes."""
    ev = db.session.get(Evaluation, evaluation_id)
    if not ev:
        flash("Evaluation not found.", "danger")
        return redirect(url_for("web.history"))
    return render_template("evaluate_wait.html", evaluation=ev)

