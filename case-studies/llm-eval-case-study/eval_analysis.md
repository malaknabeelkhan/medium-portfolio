# LLM Eval Run — Analysis Report
**4 models × 2 prompts × 30 tickets = 240 total API calls**
All 4 models ran on Colab T4 via Ollama. Zero API errors across the board.

---

## Raw Numbers at a Glance

| Model | Prompt | cat_acc | urg_exact | esc_recall | valid_json | med_lat |
|---|---|---|---|---|---|---|
| colab-qwen2.5-7b | v1 | **87%** | 50% | **93%** | 100% | 1.51s |
| colab-qwen2.5-7b | v2 | 83% | 53% | 86% | 100% | 1.46s |
| colab-qwen3-4b-2507 | v1 | 80% | **60%** | **93%** | 100% | 1.10s |
| colab-qwen3-4b-2507 | v2 | 83% | 57% | **93%** | 100% | 1.19s |
| colab-llama3.2-3b | v1 | 77% | **67%** | 86% | 100% | 1.01s |
| colab-llama3.2-3b | v2 | 80% | 53% | 86% | 100% | **0.97s** |
| colab-smollm2-1.7b | v1 | 67% | 41% | 86% | 97% | **0.99s** |
| colab-smollm2-1.7b | v2 | 70% | 37% | **100%** | 100% | **0.97s** |

---

## Metric-by-Metric Interpretation

### 1. `valid_json` — Did the model even follow format instructions?
> **All models: 97–100% ✅ Excellent**

Every model returned parseable, schema-valid JSON almost every time.
The one exception is `smollm2` on prompt_v1 (97%) — it produced 1 non-JSON
response out of 30 tickets. The fix: prompt_v2 brought it to 100%.

**Threshold to pass:** ≥ 95%. All models pass. This is the bare minimum — if
a model fails here, nothing else matters.

---

### 2. `cat_acc` — Is the model classifying tickets into the right bucket?
> **Range: 67%–87%. Mixed results ⚠️**

This is the most important metric. It tells you whether the model can correctly
distinguish Billing vs Technical Support vs Account Access vs Cancellation.

| Grade | Range | Models |
|---|---|---|
| 🟢 Good | ≥ 85% | qwen2.5-7b (v1: 87%) |
| 🟡 Acceptable | 75–84% | qwen2.5-7b v2, qwen3-4b, llama3.2-3b |
| 🔴 Weak | < 75% | smollm2-1.7b (67–70%) |

**Key insight:** 30% of tickets are misclassified by smollm2. At that error rate
it would create real operational problems (billing tickets going to tech support,
etc.). qwen2.5-7b is the clear winner here.

**Typical confusion:** The hardest tickets involve mixed intent, e.g. "I want to
cancel *because* your API keeps crashing" — models must pick the primary domain,
and smaller models tend to pick the surface word (e.g. "cancel") rather than the
root issue.

---

### 3. `urg_exact` — Does the model assign the exact urgency score?
> **Range: 37%–67%. This is the weakest metric across the board ❌**

Urgency is inherently subjective. Even humans disagree on whether a ticket is
urgency 3 vs 4. An exact-match of 50–67% on a 1–5 scale is actually expected —
it does NOT mean the model is wrong in a harmful way. What matters more is
whether the model is *off by 1* (still actionable) vs *wildly off* (urgency 1
when it should be 5).

**How to interpret:**
- **50–67%** exact → model is "one step off" on borderline tickets, which is
  normal human behavior too
- **< 40%** (smollm2 v2: 37%) → model is consistently mis-calibrated; it may
  be biasing toward a particular number

**Best performer:** llama3.2-3b on prompt_v1 at 67% — surprisingly strong for
a 3B model.

**Worst:** smollm2-1.7b on prompt_v2 at 37%. The detailed guidelines in v2
appear to *confuse* the smallest model on urgency calibration.

---

### 4. `esc_recall` — Does the model catch every ticket that needs a human?
> **Range: 86%–100%. Generally solid ✅**

This is a safety-critical metric. A **false negative** here means a ticket that
genuinely needs human attention (e.g., account compromise, production outage)
gets routed to automation and goes unresolved.

**How to read it:**
- **100%** = model never misses a ticket that needs escalation (no false
  negatives) — but may over-flag some that don't
- **86%** = model misses ~2 out of every 14 escalation-worthy tickets

| Grade | Who |
|---|---|
| 🟢 100% | smollm2 on prompt_v2 |
| 🟢 93% | qwen2.5 v1, qwen3 v1, qwen3 v2 |
| 🟡 86% | qwen2.5 v2, llama3.2 both, smollm2 v1 |

**Key insight:** In a real system you want recall ≥ 90%. 86% means roughly
1 in 7 urgent escalation tickets slips through undetected. qwen2.5-7b and
qwen3-4b-2507 on prompt_v1 both hit 93% — acceptable for a small local model.

---

### 5. `med_lat` — How fast is the model?
> **Range: 0.97s–1.51s. All fast enough for async triage ✅**

All models respond in under 2 seconds. For an asynchronous triage pipeline
(email/ticket queue) this is excellent. For real-time chat, sub-1s would be
ideal — llama3.2 and smollm2 get close.

**Speed ranking:** smollm2 ≈ llama3.2 (0.97–1.01s) > qwen3 (1.10–1.19s) >
qwen2.5 (1.46–1.51s)

> [!NOTE]
> Speed comes at a cost: smollm2 is the fastest but also the least accurate.
> qwen2.5 is slowest but most accurate. This is a classic size/quality tradeoff.

---

## Prompt v1 vs Prompt v2 — Did the Expert Prompt Help?

| Model | cat_acc Δ | urg_exact Δ | esc_recall Δ |
|---|---|---|---|
| qwen2.5-7b | -4% ⬇ | +3% ⬆ | -7% ⬇ |
| qwen3-4b-2507 | +3% ⬆ | -3% ⬇ | 0% → |
| llama3.2-3b | +3% ⬆ | -14% ⬇ | 0% → |
| smollm2-1.7b | +3% ⬆ | -4% ⬇ | +14% ⬆ |

**Verdict:** The detailed prompt (v2) **helps small models on category accuracy**
(+3% across 3 of 4 models) but **hurts urgency calibration** for most models.
This is because v2's verbose guidelines add reasoning complexity that small
models struggle to apply precisely for urgency scoring.

**Exception:** `smollm2` got a massive +14% escalation recall boost from v2,
jumping to 100% — the explicit escalation rules in v2 (security incidents,
financial disputes, etc.) appear to directly fix its blind spot.

---

## Overall Verdict — Which Model to Use?

### 🥇 Best overall: `colab-qwen2.5-7b` with `prompt_v1`
- Highest category accuracy (87%)
- Strong escalation recall (93%)
- 100% valid JSON
- Only downside: slowest at 1.51s (still fast enough)

### 🥈 Best value: `colab-qwen3-4b-2507` with `prompt_v2`
- Ties qwen2.5 on category accuracy (83%)
- Best urgency on v2 (57%)
- 93% escalation recall
- Faster than qwen2.5 (1.19s)

### ⚠️ Avoid for production: `colab-smollm2-1.7b`
- Category accuracy is 10–20pp below the others
- Urgency calibration is the worst (37–41%)
- Only 1.7B parameters — it's simply too small for nuanced 4-class triage

---

## What Would "Good" Look Like?
For a production-ready triage system, target thresholds would be:

| Metric | Minimum | Ideal |
|---|---|---|
| cat_acc | 85% | ≥ 95% |
| urg_exact | 50% | ≥ 65% |
| esc_recall | 90% | ≥ 97% |
| valid_json | 99% | 100% |
| latency | < 3s | < 1s |

**Current gap:** These are small models (1.7B–7B) running locally on a free Colab
T4. They are surprisingly capable but not production-ready without human review.
A GPT-4o or Gemini 1.5 Pro would likely hit 95%+ cat_acc and 97%+ esc_recall.
