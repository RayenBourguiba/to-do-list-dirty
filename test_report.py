import json
from pathlib import Path

import yaml


TEST_LIST_PATH = Path("test_list.yaml")
AUTO_RESULT_PATH = Path("result_test_auto.json")


def load_test_list():
    if not TEST_LIST_PATH.exists():
        raise FileNotFoundError(f"Fichier YAML introuvable : {TEST_LIST_PATH}")

    with TEST_LIST_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if isinstance(data, dict) and "tests" in data:
        return data["tests"]
    if isinstance(data, list):
        return data

    raise ValueError("Format de test_list.yaml inattendu (attendu: liste de tests).")


def load_auto_results():
    if not AUTO_RESULT_PATH.exists():
        print(f"Avertissement : fichier {AUTO_RESULT_PATH} introuvable.")
        return {}

    with AUTO_RESULT_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    tests = data.get("tests", [])
    mapping = {}

    for t in tests:
        tc_id = t.get("test_case_id") or t.get("id") or t.get("test_id")
        status = t.get("status")

        if not tc_id:
            continue

        if status in ("passed", "success", "ok", "OK"):
            norm_status = "passed"
        elif status in ("failed", "failure"):
            norm_status = "failed"
        else:
            norm_status = status or "unknown"

        mapping[tc_id] = norm_status

    return mapping


def main():
    tests = load_test_list()
    print("Lecture des tests auto via result_test_auto.json…")
    auto_results = load_auto_results()
    print("OK\n")

    total = 0
    count_passed = 0
    count_failed = 0
    count_not_found = 0
    count_manual = 0

    for test in tests:
        tc_id = (
            test.get("id")
            or test.get("test_case_id")
            or test.get("numero")
            or test.get("number")
        )
        test_type = test.get("type", "").strip().lower()

        if not tc_id:
            continue

        total += 1

        display_type = test_type
        if test_type == "auto-unittest":
            display_type = "auto"
        elif test_type == "manual":
            display_type = "manual"

        if test_type == "manual":
            status_text = "🫱  Manual test needed"
            count_manual += 1
        else:
            result = auto_results.get(tc_id)
            if result is None:
                status_text = "️Not found"
                count_not_found += 1
            elif result == "passed":
                status_text = "✅  Passed"
                count_passed += 1
            else:
                status_text = "❌  Failed"
                count_failed += 1

        print(f"{tc_id} | {display_type} | {status_text}")

    if total > 0:
        def pct(x):
            return round((x / total) * 100, 1)

        print("\n----- Summary -----")
        print(f"Number of tests: {total}")
        print(f"✅  Passed tests: {count_passed} ({pct(count_passed)}%)")
        print(f"❌  Failed tests: {count_failed} ({pct(count_failed)}%)")
        print(f"️Not found tests: {count_not_found} ({pct(count_not_found)}%)")
        print(f"🫱  Test to pass manually: {count_manual} ({pct(count_manual)}%)")
        print(
            f"✅Passed + 🫱  Manual: {count_passed + count_manual} "
            f"({pct(count_passed + count_manual)}%)"
        )
    else:
        print("Aucun test trouvé dans test_list.yaml.")


if __name__ == "__main__":
    main()
