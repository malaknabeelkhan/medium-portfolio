import os
from dotenv import load_dotenv

load_dotenv()

# MODELS is built dynamically from Colab/Ollama entries below
MODELS = []

# ── Colab / Ollama models (appended dynamically if COLAB_BASE_URL is set) ─────
colab_url = (os.getenv("COLAB_BASE_URL") or "").strip().rstrip("/")
if colab_url.endswith("/v1"):
    colab_url = colab_url[:-3]

COLAB_MODELS = [
    ("colab-qwen2.5-7b",    "qwen2.5:7b"),
    ("colab-qwen3-4b-2507", "hf.co/unsloth/Qwen3-4B-Instruct-2507-GGUF:Q4_K_M"),
    ("colab-llama3.2-3b",   "llama3.2:3b"),
    ("colab-smollm2-1.7b",  "smollm2:1.7b"),
]

for name, tag in COLAB_MODELS:
    MODELS.append({
        "name": name,
        "base_url": colab_url + "/v1" if colab_url else "",
        "api_key": "ollama",
        "model": tag,
        "delay": 1,
    })