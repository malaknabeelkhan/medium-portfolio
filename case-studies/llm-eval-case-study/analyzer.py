import csv
import glob
import json
import statistics
from collections import defaultdict

files = sorted(glob.glob("results_*.json"))
if not files:
    print("No results_*.json file found. Run run_eval.py first.")
    raise SystemExit


def is_answered(r):
    return not (r["raw_output"] or "").startswith("API_ERROR")


def rate(rows, key):
    return sum(1 for r in rows if r.get(key)) / len(rows) if rows else None


def ran_on(name):
    return "Colab T4" if name.startswith("colab") else "hosted API"


def pct(x):
    return "n/a" if x is None else f"{x:.0%}"


def sec(x):
    return "n/a" if x is None else f"{x:.2f}"


# 1. collect every model's rows from every results file
runs = defaultdict(list)
for fname in files:
    with open(fname, encoding="utf-8") as f:
        rows = json.load(f)
    by_model = defaultdict(list)
    for r in rows:
        by_model[r["model"]].append(r)
    for model, model_rows in by_model.items():
        runs[model].append((fname, model_rows))

# 2. for each model keep the run with the most answers (newest file wins a tie)
summary = []
errors = []
for model, model_runs in runs.items():
    best_file, best_rows, best_n = None, None, -1
    for fname, rows in model_runs:
        n = sum(1 for r in rows if is_answered(r))
        if n >= best_n:
            best_file, best_rows, best_n = fname, rows, n

    answered = [r for r in best_rows if is_answered(r)]
    latencies = [r["latency"] for r in answered if r.get("latency") is not None]

    summary.append({
        "model": model,
        "ran_on": ran_on(model),
        "source_file": best_file,
        "total": len(best_rows),
        "answered": len(answered),
        "strict_json": rate(answered, "strict_valid"),
        "clean_json": rate(answered, "clean_valid"),
        "category_accuracy": rate(answered, "correct"),
        "urgency_exact": rate(answered, "urgency_exact"),
        "urgency_within_1": rate(answered, "urgency_within_1"),
        "escalation_accuracy": rate(answered, "escalation_correct"),
        "median_latency_s": statistics.median(latencies) if latencies else None,
        "max_latency_s": max(latencies) if latencies else None,
    })

    for r in answered:
        if not r.get("correct"):
            errors.append({
                "model": model,
                "id": r["id"],
                "input_message": r.get("input_message", ""),
                "expected_category": r["expected"]["category"],
                "predicted_category": (r.get("predicted") or {}).get("category", "UNPARSEABLE"),
                "raw_output": r["raw_output"],
            })

# 3. print the table
header = (f"{'model':<22}{'ran_on':<12}{'ans':>7}{'strict':>8}{'clean':>7}"
          f"{'cat_acc':>9}{'urg_ex':>8}{'urg_w1':>8}{'esc':>6}{'med_s':>7}{'max_s':>7}")
print(header)
for s in summary:
    ans = f"{s['answered']}/{s['total']}"
    flag = "  <- INCOMPLETE" if s["answered"] < s["total"] else ""
    print(f"{s['model']:<22}{s['ran_on']:<12}{ans:>7}{pct(s['strict_json']):>8}"
          f"{pct(s['clean_json']):>7}{pct(s['category_accuracy']):>9}"
          f"{pct(s['urgency_exact']):>8}{pct(s['urgency_within_1']):>8}"
          f"{pct(s['escalation_accuracy']):>6}{sec(s['median_latency_s']):>7}"
          f"{sec(s['max_latency_s']):>7}{flag}")

# 4. save files you can open in Excel
with open("summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

with open("summary.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
    writer.writeheader()
    writer.writerows(summary)

if errors:
    with open("errors.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(errors[0].keys()))
        writer.writeheader()
        writer.writerows(errors)

print("\nSaved summary.csv, summary.json" + (", errors.csv" if errors else ""))