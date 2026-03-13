# 🤖 AI Coding Assistant — Scalable AI Backend System
A production-style AI backend system for generating, executing, and evaluating Python Matplotlib code using Large Language Models.

This project demonstrates modern AI backend architecture including:

- REST API design

- asynchronous task processing

- containerized deployment

- scalable AI inference pipelines

- database persistence and analytics

It integrates local LLM inference (Ollama) and cloud models (OpenAI / Anthropic) while supporting secure code execution and system analytics.

### Intelligent Code Generation & Validation
![Generation Interface & Evaluation Result](docs/screenshots/generation.gif)

*A seamless workflow: generating complex Matplotlib code via local Llama 3.2 (Ollama) and instantly verifying it through a secure, restricted execution environment.*

---
## Architecture Overview
The system follows a modern AI backend architecture with asynchronous task processing.

```text
Client
   │
   ▼
Flask API Server
   │
   ▼
Redis Task Queue
   │
   ▼
Celery Worker
   │
   ├── LLM Code Generation
   ├── Code Evaluation Sandbox
   └── Analytics Pipeline
   │
   ▼
PostgreSQL Database
```
### Key Characteristics

- Async AI processing using Celery workers
- Redis message queue for task distribution
- PostgreSQL persistence layer
- Docker containerized micro-services
- Pluggable AI model providers

## Intelligent Code Generation Workflow
Workflow:
```text
User Prompt
   │
   ▼
API Endpoint (/api/prompts)
   │
   ▼
Task queued in Redis
   │
   ▼
Celery Worker processes task
   │
   ├── Generate Matplotlib code via LLM
   ├── Execute code in restricted sandbox
   └── Store results in PostgreSQL

```
## Quick Start (Docker Recommended)


### 1. Install prerequisites
Install:

- Docker

- Docker Compose

- Ollama (for local models)

Download Ollama:

[Download and install Ollama](https://ollama.com/)

Pull the default model:
```bash
ollama pull llama3.2
```

### 2. Clone repository

```bash
git clone https://github.com/Mingyueoo/AI-Coding-Assistant-FullStack.git
cd ai_coding_assistant
```

### 3. Configure environment
Create `.env`
```bash
FLASK_ENV=development

DATABASE_URL=postgresql://ai_user:ai_password@db:5432/ai_db

REDIS_URL=redis://redis:6379/0

OLLAMA_BASE_URL=http://host.docker.internal:11434/api/generate
OLLAMA_MODEL=llama3.2

```
Optional cloud models:
```text
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```
### 4. Start the system

```bash
docker-compose up --build
```
Services started:
```text
web      → Flask API server
worker   → Celery AI worker
db       → PostgreSQL
redis    → task queue
```
Open:
```text
http://localhost:5000
```



---

## Project Structure

```
ai_coding_assistant/

├── Dockerfile
├── docker-compose.yaml
├── run.py
├── seed_data.py
├── requirements.txt
├── .env

└── app/
    ├── app.py
    ├── db.py

    ├── models/
    │   ├── prompt.py
    │   ├── generation.py
    │   └── evaluation.py

    ├── routes/
    │   ├── api.py
    │   └── web.py

    ├── services/
    │   ├── model_service.py
    │   ├── evaluation_service.py
    │   └── analytics_service.py

    ├── workers/
    │   ├── celery_app.py
    │   └── tasks.py

    ├── templates/
    └── static/
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
```text
POST /api/prompts
```

```bash
curl -X POST http://localhost:5000/api/prompts \
-H "Content-Type: application/json" \
-d '{"prompt_text":"plot a bar chart","model_name":"ollama-llama"}'
```
Response:
```json
{
 "prompt_id":1,
 "generation_id":1,
 "task_id":"af12c98",
 "status":"queued"
}
```
The AI pipeline runs asynchronously in the Celery worker.

---

## Supported Models

| Model            | Description                      |
| ---------------- | -------------------------------- |
| mock-gpt         | Simulated model for fast testing |
| ollama-llama     | Local Llama 3.2 via Ollama       |
| openai-gpt4      | OpenAI GPT models                |
| anthropic-claude | Anthropic Claude                 |


---

## Database Schema

```text
Prompt
 └── Generation
        └── Evaluation
```

```text
Prompt
(id, prompt_text, model_name, created_at)

Generation
(id, prompt_id, generated_code, status, created_at)

Evaluation
(id, generation_id, result, error_message, created_at)
```

Statuses:
```text
pending
generated
failed
```

Evaluation results:
```text
correct
partially_correct
failed
```
---

## Analytics

System analytics includes:

- model success rate

- error distribution

- prompt usage statistics

Powered by:
```text
Pandas
SQLAlchemy
Matplotlib
```

## Technology Stack
### Backend

- Flask

- SQLAlchemy

- Celery

- Redis

### Infrastructure

- Docker

- Docker Compose

- PostgreSQL

### AI / ML

- Ollama

- OpenAI API

- Anthropic Claude

### Data & Visualization

- Pandas

- Matplotlib

- Frontend

- Jinja2

- Bootstrap

---

## Engineering Highlights

This project demonstrates several real-world backend engineering patterns:

### AI Backend Architecture

- async AI task processing

- queue-based job execution

- scalable worker architecture

### Production Infrastructure

- containerized services

- environment-based configuration

- persistent database layer

### Safe Code Execution

- AST parsing

- restricted execution environment

- error classification

---
## Portfolio Context

This project was built to demonstrate AI backend engineering skills, including:

- LLM system integration

- asynchronous processing pipelines

- containerized deployment

- database-driven AI services
