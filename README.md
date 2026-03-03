# 🤖 AI Coding Assistant — Full-Stack Python System

A production-grade Flask web application for AI-powered Matplotlib code generation, evaluation, and analytics. Built to demonstrate full-stack Python engineering: REST API design, database persistence, local/cloud LLM integration (Ollama/OpenAI), code execution/evaluation, and data analytics.
### Intelligent Code Generation & Validation
![Generation Interface & Evaluation Result](docs/screenshots/generation.gif)

*A seamless workflow: generating complex Matplotlib code via local Llama 3.2 (Ollama) and instantly verifying it through a secure, restricted execution environment.*

---

## Quick Start

### 1. Set up Local AI (Ollama)
This project uses Ollama for free, local inference.

[Download and install Ollama](https://ollama.com/)

Pull the default model:
```bash
ollama pull llama3.2
```

### 2. Clone & set up environment

```bash
git clone https://github.com/Mingyueoo/AI-Coding-Assistant-FullStack.git
cd ai_coding_assistant

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env
# Edit .env if needed (works out of the box with mock models)

```

### 4. Run the app

```bash
python run.py
```

Open **http://localhost:5000**

### 5. (Optional) Seed demo data

```bash
python seed_data.py
```

---

## Project Structure

```
ai_coding_assistant/
├── run.py                      # Entry point
├── seed_data.py                # Demo data seeder
├── requirements.txt
├── .env
└── app/
    ├── app.py                  # Flask app factory
    ├── db.py                   # SQLAlchemy instance
    ├── models/
    │   ├── prompt.py           # Prompt table
    │   ├── generation.py       # Generation table
    │   └── evaluation.py       # Evaluation table
    ├── routes/
    │   ├── api.py              # REST API blueprints
    │   └── web.py              # HTML page blueprints
    ├── services/
    │   ├── model_service.py    # Code generation (mock + real models)
    │   ├── evaluation_service.py # Safe code execution & evaluation
    │   └── analytics_service.py  # Pandas/SQLAlchemy analytics + charts
    ├── templates/
    │   ├── base.html
    │   ├── index.html          # Home / generator
    │   ├── result.html         # Code output + evaluation
    │   ├── history.html        # Paginated prompt history
    │   └── dashboard.html      # Analytics dashboard
    └── static/
        ├── css/style.css
        └── js/app.js
```

---

## REST API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/prompts` | Create prompt & generate code |
| `GET` | `/api/prompts` | List prompts (paginated, filterable) |
| `GET` | `/api/prompts/{id}` | Get single prompt with generations |
| `POST` | `/api/prompts/{id}/evaluate` | Evaluate generated code |
| `GET` | `/api/analytics` | System analytics (JSON) |

### Example: Generate Code

```bash
curl -X POST http://localhost:5000/api/prompts \
  -H "Content-Type: application/json" \
  -d '{"prompt_text": "plot a bar chart of monthly revenue", "model_name": "mock-gpt"}'
```

```json
{
  "prompt_id": 1,
  "generation_id": 1,
  "generated_code": "import matplotlib.pyplot as plt\n...",
  "status": "generated"
}
```

### Example: Evaluate Code

```bash
curl -X POST http://localhost:5000/api/prompts/1/evaluate
```

```json
{
  "evaluation_id": 1,
  "evaluation_result": "correct",
  "error_message": null
}
```

### Example: Paginated History

```bash
curl "http://localhost:5000/api/prompts?page=1&per_page=5&model_name=mock-gpt"
```

### Example: Analytics

```bash
curl http://localhost:5000/api/analytics
```

---

## Supported Models

| Model | Description                                                 |
|-------|-------------------------------------------------------------|
| `mock-gpt` | Simulated GPT — generates correct templates instantly       |
| `ollama-llama` | Local model — lama 3.2 running via Ollama. Private and free |
| `openai-gpt4` | Real OpenAI GPT-4o (requires `OPENAI_API_KEY`)              |
| `anthropic-claude` | Real Claude (requires `ANTHROPIC_API_KEY`)                  |

---

## Database Schema

```
Prompt (id, prompt_text, model_name, created_at)
   └─→ Generation (id, prompt_id FK, generated_code, status, created_at)
            └─→ Evaluation (id, generation_id FK, result, error_message, created_at)
```

- **result**: `correct` | `partially_correct` | `failed`
- **status**: `pending` | `generated` | `failed`

---

## Features

- **Code Generation** — Template-based mock models + real LLM integration
- **Code Evaluation** — Safe AST parse + restricted exec with error classification
- **REST API** — Full CRUD with pagination and filtering
- **Analytics** — Pandas aggregation: success rates, per-model accuracy, error distribution
- **Dashboard** — Live Matplotlib charts rendered as base64 PNG
- **History** — Searchable, paginated, filterable prompt history

---

## Configuration (`.env`)

```env
# --- Flask Basic Configuration ---
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///ai_coding_assistant.db

# --- Ollama (Local AI) ---
DEFAULT_MODEL=ollama-llama

# --- Cloud API Configuration (Optional) ---
# Uncomment to use OpenAI
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

---

## Tech Stack

- **Backend**: Flask 3, SQLAlchemy 2, Flask-SQLAlchemy
- **AI/Inference**: Ollama (Llama 3.2), OpenAI API
- **Data**: Pandas, Matplotlib
- **Frontend**: Jinja2, Bootstrap 5, Bootstrap Icons
- **Storage**: SQLite (default), PostgreSQL-compatible via `DATABASE_URL`
