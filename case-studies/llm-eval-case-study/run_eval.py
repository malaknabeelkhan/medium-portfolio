import json
import time
import statistics
from pydantic import ValidationError
from models import MODELS
from llm_client import ask_model
from schema import TicketResult
import sys

wanted = sys.argv[1:]   # optional model-name filter: python run_eval.py colab

# ── System prompts ─────────────────────────────────────────────────────────────
# Schema (schema.TicketResult):
#   category                 : Literal["Billing","Technical Support","Account Access","Cancellation"]
#   urgency                  : int  ge=1, le=5
#   requires_human_escalation: bool

PROMPTS = {
    "prompt_v1": """You are a customer support triage system.
Read the customer message and reply with ONLY a valid JSON object — no markdown, no extra text.
The JSON must contain exactly these three fields:

  "category"                  — one of (case-sensitive, pick exactly one):
                                   "Billing"
                                   "Technical Support"
                                   "Account Access"
                                   "Cancellation"
  "urgency"                   — an integer between 1 and 5 (1 = lowest, 5 = highest)
  "requires_human_escalation" — a JSON boolean: true or false

Example of a valid response:
{"category": "Billing", "urgency": 4, "requires_human_escalation": true}""",

    "prompt_v2": """You are an expert enterprise customer support triage assistant. Analyze the incoming customer message and classify it according to the schema below.

Output Requirement:
Return ONLY a single valid JSON object and nothing else. Do not use markdown code blocks (e.g., no ```json), do not include introductory or concluding text, and provide no explanations.

Schema:
{
  "category": "Billing" | "Technical Support" | "Account Access" | "Cancellation",
  "urgency": <integer from 1 to 5>,
  "requires_human_escalation": <true or false>
}

---

Classification Guidelines:

1. Category Selection (Choose the most appropriate primary domain):
   - Cancellation: The user's primary request is to terminate, close, or downgrade their subscription, account, or contract.
   - Technical Support: The core issue involves software bugs, system errors (e.g., 500/404 errors, outages), API behavior, feature malfunctions, performance degradation, or technical how-to/implementation questions.
   - Account Access: Issues involving authentication, passwords, 2FA failures, account lockouts, unauthorized access, team permissions, or workspace ownership transfer.
   - Billing: Inquiries regarding charges, invoices, payment methods, refund requests, pricing, or subscription plan adjustments.
   *Tie-breaker for mixed-intent:* If a ticket combines a technical failure with a cancellation threat, classify it based on what team needs to act first to resolve the root issue (e.g., fixing a bug vs processing a cancellation).

2. Urgency Scale (1 to 5):
   - 1: General informational questions, minor feedback, or inquiries with no time pressure.
   - 2: Routine requests or non-critical questions that can wait a few days.
   - 3: Moderate inconvenience where a temporary workaround exists.
   - 4: User is completely blocked from performing a core task, financial stakes are involved, or the customer displays strong frustration.
   - 5: Critical production outage, active security breach/account compromise, or a total block with an immediate, high-stakes deadline.

3. Human Escalation (requires_human_escalation: true if any apply, otherwise false):
   - Security incidents, suspected account takeovers, or data privacy concerns.
   - System-wide outages or entire team blockages.
   - Disputed financial charges with explicit, immediate refund demands.
   - High-churn risk situations (e.g., threats to leave driven by unresolved recurring failures).
   - Actions requiring administrative approval or manual agent intervention (e.g., ownership transfers, exception refunds).

---

Example Output Format (Values are structural placeholders only):
{"category": "Billing", "urgency": 2, "requires_human_escalation": false}""",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def strip_fences(text):
    """Remove a ```json ... ``` wrapper if the model added one."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]   # drop the first line (```json)
        text = text.rsplit("```", 1)[0]  # drop the closing fence
    return text.strip()


def pct(x):
    return "n/a" if x is None else f"{x:.0%}"


# ── Load dataset ───────────────────────────────────────────────────────────────

with open("golden_dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

all_results = []
summary = []          # one entry per (model, prompt_id) combination

# ── Main eval loop ─────────────────────────────────────────────────────────────

for config in MODELS:
    if wanted and not any(w in config["name"] for w in wanted):
        continue
    if not config["api_key"] or config["base_url"] in ("", "/v1"):
        print("Skipping", config["name"], "(no key or URL yet)")
        continue

    delay = config.get("delay", 4)

    for prompt_id, system_prompt in PROMPTS.items():
        print(f"Running  {config['name']}  [{prompt_id}] ...")

        answered = strict_count = clean_count = correct_count = api_errors = 0
        urgency_exact_count = escalation_correct_count = 0
        escalation_tp = escalation_fn = 0   # for recall: TP / (TP + FN)
        latencies = []

        for item in dataset:
            expected = item["expected_output"]
            record = {
                "model":         config["name"],
                "prompt_id":     prompt_id,
                "id":            item["id"],
                "input_message": item["input_message"],
                "expected":      expected,
                "raw_output":    None,
                "strict_valid":  False,
                "clean_valid":   False,
                "predicted":     None,
                "correct":       False,
                "latency":       None,
            }

            try:
                raw, latency = ask_model(config, item["input_message"], system_prompt)
            except Exception as e:
                api_errors += 1
                record["raw_output"] = f"API_ERROR: {e}"
                all_results.append(record)
                time.sleep(delay)
                continue

            answered += 1
            record["raw_output"] = raw
            record["latency"]    = latency
            latencies.append(latency)

            try:  # strict: raw text must be valid JSON + valid schema as-is
                TicketResult.model_validate_json(raw)
                record["strict_valid"] = True
                strict_count += 1
            except (ValidationError, ValueError):
                # ValueError covers json.JSONDecodeError (malformed JSON)
                pass

            try:  # clean: allow a markdown fence around the JSON
                parsed = TicketResult.model_validate_json(strip_fences(raw))
                record["clean_valid"] = True
                clean_count += 1
                record["predicted"] = parsed.model_dump()

                # category: Literal["Billing","Technical Support","Account Access","Cancellation"]
                if parsed.category == expected["category"]:
                    record["correct"] = True
                    correct_count += 1

                # urgency: int ge=1 le=5  (Pydantic already enforced bounds above)
                record["urgency_exact"]   = parsed.urgency == expected["urgency"]
                record["urgency_within_1"] = abs(parsed.urgency - expected["urgency"]) <= 1

                # requires_human_escalation: bool  (Pydantic already enforced type above)
                record["escalation_correct"] = (
                    parsed.requires_human_escalation == expected["requires_human_escalation"]
                )

                if record["urgency_exact"]:
                    urgency_exact_count += 1
                if record["escalation_correct"]:
                    escalation_correct_count += 1

                # Escalation recall: among tickets that truly need human action,
                # how many did the model correctly flag?
                if expected["requires_human_escalation"]:
                    if parsed.requires_human_escalation:
                        escalation_tp += 1
                    else:
                        escalation_fn += 1

            except (ValidationError, ValueError):
                # ValidationError → field value violates schema constraints
                # ValueError      → json.JSONDecodeError after fence strip
                pass

            all_results.append(record)
            time.sleep(delay)

        summary.append({
            "model":               config["name"],
            "prompt_id":           prompt_id,
            "answered":            answered,
            "strict_json":         strict_count / answered if answered else None,
            "clean_json":          clean_count  / answered if answered else None,
            "category_accuracy":   correct_count / answered if answered else None,
            "urgency_exact":       urgency_exact_count / clean_count if clean_count else None,
            "escalation_accuracy": escalation_correct_count / clean_count if clean_count else None,
            "escalation_recall": (
                escalation_tp / (escalation_tp + escalation_fn)
                if (escalation_tp + escalation_fn) > 0 else None
            ),
            "median_latency":      statistics.median(latencies) if latencies else None,
            "api_errors":          api_errors,
        })

# ── Live progress table (one row per model×prompt) ─────────────────────────────
print()
print(f"{'model':<22}{'prompt':<12}{'answered':>9}{'strict':>8}{'clean':>7}{'acc':>6}{'med_s':>7}{'errs':>6}")
print("-" * 80)
for s in summary:
    lat = "n/a" if s["median_latency"] is None else f"{s['median_latency']:.2f}"
    print(
        f"{s['model']:<22}{s['prompt_id']:<12}{s['answered']:>9}"
        f"{pct(s['strict_json']):>8}{pct(s['clean_json']):>7}"
        f"{pct(s['category_accuracy']):>6}{lat:>7}{s['api_errors']:>6}"
    )

# ── Final metrics table grouped by prompt ──────────────────────────────────────
print()
for pid in PROMPTS:
    rows = [s for s in summary if s["prompt_id"] == pid]
    if not rows:
        continue
    print("=" * 85)
    print(f"  FINAL METRICS  —  {pid}")
    print("=" * 85)
    print(
        f"{'model':<26}{'cat_acc':>9}{'urg_exact':>10}"
        f"{'esc_recall':>11}{'valid_json':>11}{'med_lat_s':>10}"
    )
    print("-" * 85)
    for s in rows:
        lat = "n/a" if s["median_latency"] is None else f"{s['median_latency']:.2f}s"
        print(
            f"{s['model']:<26}"
            f"{pct(s['category_accuracy']):>9}"
            f"{pct(s['urgency_exact']):>10}"
            f"{pct(s['escalation_recall']):>11}"
            f"{pct(s['clean_json']):>11}"
            f"{lat:>10}"
        )
    print()

print("Metric definitions:")
print("  cat_acc     – category accuracy          (correct / answered)")
print("  urg_exact   – urgency exact-match rate   (matched / valid-JSON answers)")
print("  esc_recall  – escalation recall          (TP / (TP + FN) on tickets needing escalation)")
print("  valid_json  – valid JSON rate            (clean parses / answered, fences stripped)")
print("  med_lat_s   – median response latency    (seconds)")

# ── Save raw results ───────────────────────────────────────────────────────────
filename = time.strftime("results_%Y%m%d_%H%M%S.json")
with open(filename, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2)
print("\nSaved every answer to", filename)
