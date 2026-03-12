# @Version :1.0
# @Author  : Mingyue
# @File    : model_service.py.py
# @Time    : 02/03/2026 19:49
import os
import logging
import random
import requests

logger = logging.getLogger(__name__)

SUPPORTED_MODELS = ["mock-gpt","ollama-llama", "openai-gpt4", "anthropic-claude","mock-codellama"]

# Template library for mock generation
MOCK_TEMPLATES = {
    "bar": """import matplotlib.pyplot as plt
import numpy as np

categories = ['A', 'B', 'C', 'D', 'E']
values = np.random.randint(10, 100, size=5)

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(categories, values, color='steelblue', edgecolor='white', linewidth=0.7)
ax.bar_label(bars, padding=3)
ax.set_xlabel('Category')
ax.set_ylabel('Value')
ax.set_title('Bar Chart')
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig('output.png', dpi=150)
plt.show()
""",
    "horizontal bar": """import matplotlib.pyplot as plt
import numpy as np

categories = ['Category A', 'Category B', 'Category C', 'Category D']
values = np.random.randint(20, 100, size=4)

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(categories, values, color='coral', edgecolor='white')
ax.bar_label(bars, padding=3)
ax.set_xlabel('Value')
ax.set_title('Horizontal Bar Chart')
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig('output.png', dpi=150)
plt.show()
""",
    "line": """import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, y1, label='sin(x)', linewidth=2)
ax.plot(x, y2, label='cos(x)', linewidth=2, linestyle='--')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Line Chart')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output.png', dpi=150)
plt.show()
""",
    "scatter": """import matplotlib.pyplot as plt
import numpy as np

np.random.seed(42)
x = np.random.randn(100)
y = x * 1.5 + np.random.randn(100) * 0.5
colors = np.random.rand(100)

fig, ax = plt.subplots(figsize=(7, 6))
sc = ax.scatter(x, y, c=colors, cmap='viridis', alpha=0.7, s=60)
plt.colorbar(sc, ax=ax, label='Color Scale')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Scatter Plot')
plt.tight_layout()
plt.savefig('output.png', dpi=150)
plt.show()
""",
    "pie": """import matplotlib.pyplot as plt

labels = ['Python', 'JavaScript', 'Java', 'C++', 'Other']
sizes = [35, 25, 20, 12, 8]
explode = (0.05, 0, 0, 0, 0)

fig, ax = plt.subplots(figsize=(7, 6))
ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
       shadow=True, startangle=140)
ax.set_title('Programming Language Usage')
plt.tight_layout()
plt.savefig('output.png', dpi=150)
plt.show()
""",
    "histogram": """import matplotlib.pyplot as plt
import numpy as np

np.random.seed(0)
data = np.random.normal(loc=50, scale=15, size=500)

fig, ax = plt.subplots(figsize=(8, 5))
n, bins, patches = ax.hist(data, bins=30, color='steelblue', edgecolor='white', alpha=0.8)
ax.set_xlabel('Value')
ax.set_ylabel('Frequency')
ax.set_title('Histogram of Normal Distribution')
ax.axvline(data.mean(), color='red', linestyle='--', label=f'Mean: {data.mean():.1f}')
ax.legend()
plt.tight_layout()
plt.savefig('output.png', dpi=150)
plt.show()
""",
    "heatmap": """import matplotlib.pyplot as plt
import numpy as np

np.random.seed(1)
data = np.random.rand(8, 8)
row_labels = [f'Row {i+1}' for i in range(8)]
col_labels = [f'Col {i+1}' for i in range(8)]

fig, ax = plt.subplots(figsize=(8, 7))
im = ax.imshow(data, cmap='YlOrRd')
plt.colorbar(im, ax=ax)
ax.set_xticks(range(8))
ax.set_yticks(range(8))
ax.set_xticklabels(col_labels, rotation=45)
ax.set_yticklabels(row_labels)
ax.set_title('Heatmap')
plt.tight_layout()
plt.savefig('output.png', dpi=150)
plt.show()
""",
    "default": """import matplotlib.pyplot as plt
import numpy as np

x = np.arange(1, 7)
y = np.array([4, 7, 2, 9, 5, 8])

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, y, marker='o', linewidth=2, color='steelblue', markersize=8)
ax.fill_between(x, y, alpha=0.2, color='steelblue')
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_title('Generated Chart')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('output.png', dpi=150)
plt.show()
""",
}


def _detect_chart_type(prompt_text: str) -> str:
    prompt_lower = prompt_text.lower()
    for key in MOCK_TEMPLATES:
        if key != "default" and key in prompt_lower:
            return key
    return "default"

def _ollama_generate(prompt_text: str) -> str:
    """Use the local Ollama API to generate code"""
    url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/api/generate")
    model_name = os.environ.get("OLLAMA_MODEL", "llama3.2")

    # Building Prompt Enhancements for Plotting Tasks
    refined_prompt = (
        f"You are a Python expert. Generate ONLY clean, runnable Matplotlib code for the following request: {prompt_text}. "
        "Do not include any explanations, markdown code blocks, or comments outside the code."
    )

    payload = {
        "model": model_name,
        "prompt": refined_prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,  # Reduce randomness and ensure code stability
            "num_predict": 1024
        }
    }

    try:
        logger.info(f"Connecting to Ollama at {url} using model {model_name}...")
        response = requests.post(url, json=payload, timeout=90)  # Local models may be slow; set a long timeout.
        response.raise_for_status()

        result = response.json()
        generated_code = result.get("response", "").strip()

        # Clean up any existing Markdown tags (such as ```python`)
        if "```" in generated_code:
            generated_code = generated_code.split("```")[1]
            if generated_code.startswith("python"):
                generated_code = generated_code[6:]

        return generated_code.strip()

    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama connection failed: {e}")
        raise RuntimeError(f"Could not connect to Ollama. Is it running? Error: {e}")

def _mock_generate(prompt_text: str, model_name: str) -> str:
    """Simulate code generation with realistic templates."""
    chart_type = _detect_chart_type(prompt_text)
    logger.info(f"[MockModel:{model_name}] Detected chart type: {chart_type}")
    # Occasionally inject a minor bug for realism
    if model_name == "mock-codellama" and random.random() < 0.15:
        code = MOCK_TEMPLATES[chart_type]
        code = code.replace("plt.show()", "plt.shw()  # typo introduced")
        return code
    return MOCK_TEMPLATES[chart_type]


def _openai_generate(prompt_text: str) -> str:
    try:
        import openai
        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        system = (
            "You are an expert Python data visualization assistant. "
            "Generate clean, runnable Matplotlib code. Output ONLY the Python code, no explanation."
        )
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"Generate Matplotlib code for: {prompt_text}"},
            ],
            max_tokens=800,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"OpenAI generation failed: {e}")


def _anthropic_generate(prompt_text: str) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        resp = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=800,
            system=(
                "You are an expert Python data visualization assistant. "
                "Generate clean, runnable Matplotlib code. Output ONLY the Python code, no explanation."
            ),
            messages=[{"role": "user", "content": f"Generate Matplotlib code for: {prompt_text}"}],
        )
        return resp.content[0].text.strip()
    except Exception as e:
        raise RuntimeError(f"Anthropic generation failed: {e}")


def generate_code(prompt_text: str, model_name: str) -> str:
    """
    Main entry point for code generation.
    Routes to appropriate backend based on model_name.
    """
    logger.info(f"Generating code | model={model_name} | prompt={prompt_text[:60]}")

    if model_name in ("mock-gpt", "mock-codellama"):
        return _mock_generate(prompt_text, model_name)
    elif model_name == "ollama-llama":
        return _ollama_generate(prompt_text)
    elif model_name == "openai-gpt4":
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not set in environment.")
        return _openai_generate(prompt_text)
    elif model_name == "anthropic-claude":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY not set in environment.")
        return _anthropic_generate(prompt_text)
    else:
        logger.warning(f"Unknown model '{model_name}', falling back to mock-gpt")
        return _mock_generate(prompt_text, "mock-gpt")