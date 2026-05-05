import json
import os
from datetime import datetime

RESULTS_DIR = os.path.join("data", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def load_last_results():
    files = sorted(
        [f for f in os.listdir(RESULTS_DIR) if f.endswith(".json")],
        reverse=True,
    )
    if not files:
        return None
    with open(os.path.join(RESULTS_DIR, files[0]), "r", encoding="utf-8") as f:
        return json.load(f)


def save_results(data):
    today = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(RESULTS_DIR, f"{today}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n[COMPARATOR] Resultados salvos em {path}")
    return path


def compare_with_last(current, last):
    if not last:
        return {"new": current.get("programs", []), "closed": [], "changed": []}

    last_map = {}
    for p in last.get("programs", []):
        key = p["program_name"].lower().strip()
        last_map[key] = p

    new_programs = []
    closed_programs = []
    changed_programs = []

    for p in current.get("programs", []):
        key = p["program_name"].lower().strip()
        if key not in last_map:
            new_programs.append(p)
        else:
            old = last_map[key]
            if old.get("status") != p.get("status"):
                changed_programs.append({
                    "program": p,
                    "old_status": old.get("status"),
                    "new_status": p.get("status"),
                })
            elif old.get("deadline") != p.get("deadline"):
                changed_programs.append({
                    "program": p,
                    "old_status": old.get("status"),
                    "new_status": p.get("status"),
                    "change": "deadline_alterada",
                    "old_deadline": old.get("deadline"),
                    "new_deadline": p.get("deadline"),
                })

    current_map = {p["program_name"].lower().strip(): p for p in current.get("programs", [])}
    for key, old in last_map.items():
        if key not in current_map and old.get("status") == "aberta":
            closed_programs.append(old)

    return {"new": new_programs, "closed": closed_programs, "changed": changed_programs}
