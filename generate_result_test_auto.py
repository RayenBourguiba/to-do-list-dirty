import json
from pathlib import Path
import os

import django
from django.conf import settings
from django.test.utils import get_runner

BASE_DIR = Path(__file__).resolve().parent
AUTO_RESULT_PATH = BASE_DIR / "result_test_auto.json"
TEST_LIST_PATH = BASE_DIR / "test_list.yaml"


def load_auto_test_ids():
    """Retourne la liste des IDs de tests auto depuis test_list.yaml."""
    import yaml

    if not TEST_LIST_PATH.exists():
        return []

    with TEST_LIST_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if isinstance(data, dict) and "tests" in data:
        tests = data["tests"]
    else:
        tests = data

    ids = []
    for t in tests:
        tc_id = (
            t.get("id")
            or t.get("test_case_id")
            or t.get("numero")
            or t.get("number")
        )
        t_type = (t.get("type") or "").strip().lower()
        if tc_id and t_type in ("auto", "auto-unittest"):
            ids.append(tc_id)

    return ids


def run_tests_and_save_results():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todo.settings")
    django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=False)

    failures = test_runner.run_tests(["tasks"])

    total_tests = getattr(test_runner, "tests_run", 0)
    global_status = "passed" if failures == 0 else "failed"

    auto_test_ids = load_auto_test_ids()

    tests_entries = []
    for tc_id in auto_test_ids:
        tests_entries.append(
            {
                "test_case_id": tc_id,
                "status": global_status,
            }
        )

    result_data = {
        "total_tests": total_tests,
        "failures": failures,
        "errors": [],
        "success": total_tests if failures == 0 else (total_tests - failures),
        "tests": tests_entries,
    }

    with AUTO_RESULT_PATH.open("w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=4, ensure_ascii=False)

    print(f"Résultats des tests auto enregistrés dans {AUTO_RESULT_PATH}")


if __name__ == "__main__":
    run_tests_and_save_results()
