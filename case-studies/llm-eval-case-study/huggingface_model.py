# from huggingface_hub import list_models

# models = list_models(
#     pipeline_tag="text-generation",
#     search="instruct",
#     sort="downloads",
#     limit=100,
# )
# for m in models:
#     print(m.id, m.downloads, m.likes)


# import re
# from huggingface_hub import list_models

# BAD_WORDS = ["awq", "gptq", "fp8", "gguf", "nvfp4", "4bit", "int4", "int8",
#              "w4a16", "quantized", "mlx", "coder", "-vl", "math", "guard", "llada"]
# REPACKAGERS = ["unsloth/", "bartowski/", "nousresearch/", "nm-testing/", "redhatai/",
#                "cyankiwi/", "quanttrio/", "stelterlab/", "orion-zhen/",
#                "casperhansen/", "hugging-quants/", "mlx-community/", "nvidia/"]


# def size_in_billions(name):
#     # finds things like "7b" or "135m" in the model name
#     match = re.search(r"(\d+(?:\.\d+)?)([bm])(?![a-z])", name)
#     if not match:
#         return None
#     value = float(match.group(1))
#     return value if match.group(2) == "b" else value / 1000


# models = list_models(
#     pipeline_tag="text-generation", search="instruct", sort="downloads", limit=100
# )

# shortlist = []
# for m in models:
#     name = m.id.lower()
#     if any(word in name for word in BAD_WORDS):
#         continue
#     if any(name.startswith(r) for r in REPACKAGERS):
#         continue
#     size = size_in_billions(name)
#     if size is not None and not (1 <= size <= 9):
#         continue  # too tiny or too big for a free T4
#     shortlist.append(m)

# print(len(shortlist), "models left")
# for m in shortlist:
#     print(m.id, m.downloads)




import re
import csv
from huggingface_hub import HfApi

# -----------------------------
# Configuration
# -----------------------------
MAX_PARAMETERS_B = 6
MIN_PARAMETERS_B = 0.1
MODEL_LIMIT = 100

BAD_WORDS = [
    "awq", "gptq", "fp8", "gguf", "nvfp4", "4bit", "int4",
    "int8", "w4a16", "quantized", "mlx", "coder", "-vl",
    "math", "guard", "llada"
]

REPACKAGERS = [
    "unsloth/", "bartowski/", "nousresearch/", "nm-testing/",
    "redhatai/", "cyankiwi/", "quanttrio/", "stelterlab/",
    "orion-zhen/", "casperhansen/", "hugging-quants/",
    "mlx-community/", "nvidia/"
]

api = HfApi()


# -----------------------------
# Helper functions
# -----------------------------
def size_in_billions(name, model_info=None):
    """Find model size from metadata first, then model ID."""
    safe = getattr(
        getattr(model_info, "safetensors", None),
        "total", None
    )

    if isinstance(safe, dict):
        safe = safe.get("parameters")

    if isinstance(safe, (int, float)) and safe > 0:
        return safe / 1_000_000_000

    # Match examples: 1B, 1.5B, 500M
    match = re.search(
        r"(?<![a-z0-9])(\d+(?:\.\d+)?)\s*([bm])"
        r"(?![a-z0-9])",
        name.lower()
    )

    if not match:
        return None

    value = float(match.group(1))
    return value if match.group(2) == "b" else value / 1000


def get_context_window(config):
    """Extract context-length hints from model config."""
    if not isinstance(config, dict):
        return "Unknown"

    possible_keys = [
        "max_position_embeddings",
        "max_sequence_length",
        "seq_length",
        "model_max_length",
        "max_seq_len",
        "n_positions"
    ]

    for key in possible_keys:
        value = config.get(key)

        if isinstance(value, int) and 0 < value < 10_000_000:
            return value

    # Some architectures keep this in nested configs.
    for value in config.values():
        if isinstance(value, dict):
            result = get_context_window(value)
            if result != "Unknown":
                return result

    return "Unknown"


def get_company(model):
    """Organization is usually the part before the slash."""
    return model.id.split("/")[0] if "/" in model.id else "Unknown"


def get_family(model_id):
    """Estimate family from model ID; not guaranteed."""
    name = model_id.split("/")[-1]

    patterns = [
        "Qwen", "Llama", "Mistral", "Phi", "Gemma",
        "Granite", "SmolLM", "OLMo", "EXAONE",
        "EuroLLM", "OpenELM", "Kimi", "Apertus"
    ]

    for family in patterns:
        if family.lower() in name.lower():
            return family

    return "Other / Unknown"


def get_instruction_status(model):
    """Infer instruction tuning from ID and tags."""
    text = (model.id + " " + " ".join(model.tags or [])).lower()

    if any(x in text for x in ["instruct", "instruction-tuned", "-it", "chat"]):
        return "Likely instruction-tuned"

    return "Not confirmed"


def get_license(model):
    card = getattr(model, "card_data", None)
    return getattr(card, "license", None) or "Unknown"


# -----------------------------
# Search models
# -----------------------------
models = api.list_models(
    pipeline_tag="text-generation",
    search="instruct",
    sort="downloads",
    direction=-1,
    limit=MODEL_LIMIT,
    cardData=True,
    fetch_config=True,
)

results = []
seen = set()

for model in models:
    name = model.id.lower()

    if model.id in seen:
        continue
    seen.add(model.id)

    if any(word in name for word in BAD_WORDS):
        continue

    if any(name.startswith(prefix) for prefix in REPACKAGERS):
        continue

    size = size_in_billions(model.id, model)

    # Keep only models with a known size under 6B.
    # Name-based estimates may be approximate.
    if size is None or not (MIN_PARAMETERS_B <= size < MAX_PARAMETERS_B):
        continue

    config = getattr(model, "config", None) or {}
    context = get_context_window(config)

    results.append({
        "model": model.id,
        "parameters_B": round(size, 2),
        "company_or_org": get_company(model),
        "family": get_family(model.id),
        "instruction_tuned": get_instruction_status(model),
        "context_window_tokens": context,
        "downloads": model.downloads or 0,
        "likes": model.likes or 0,
        "pipeline": model.pipeline_tag or "Unknown",
        "license": get_license(model),
        "gated": getattr(model, "gated", None),
        "last_modified": str(model.last_modified or "Unknown"),
        "model_url": f"https://huggingface.co/{model.id}",
    })

# Sort by popularity
results.sort(key=lambda row: row["downloads"], reverse=True)

# -----------------------------
# Display and save
# -----------------------------
print(f"\nFound {len(results)} candidate models under 6B parameters.\n")

for rank, row in enumerate(results, start=1):
    print(f"\n{'=' * 65}")
    print(f"Rank: {rank}")
    for key, value in row.items():
        print(f"{key}: {value}")

# Save results for spreadsheet study
if results:
    with open("huggingface_models_under_6b.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print("\nSaved: huggingface_models_under_6b.csv")
