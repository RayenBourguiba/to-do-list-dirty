import json
from pathlib import Path
from .models import Task


def import_tasks_from_dataset():
    dataset_path = Path(__file__).resolve().parent / "dataset.json"

    with dataset_path.open(encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        title = item["title"]
        complete = item.get("complete", False)

        Task.objects.get_or_create(
            title=title,
            defaults={"complete": complete},
        )
