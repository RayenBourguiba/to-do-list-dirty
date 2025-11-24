import json
from django.test import TestCase
from django.urls import reverse
from tasks.models import Task
from pathlib import Path
from tasks.utils import import_tasks_from_dataset


class TestTaskViews(TestCase):
    def setUp(self):
        self.task = Task.objects.create(
            title="Test task",
            complete=False,
        )

    def test_home_page_post_creates_task(self):
        url = reverse("list")
        payload = {
            "title": "Created via POST"
        }

        response = self.client.post(url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")

        self.assertTrue(Task.objects.filter(title="Created via POST").exists())

    def test_home_page_post_invalid_does_not_create_task(self):
        url = reverse("list")
        initial_count = Task.objects.count()

        payload = { "title": "" }

        response = self.client.post(url, data=payload)

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Task.objects.count(), initial_count)

    def test_home_page_get(self):
        url = reverse("list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/list.html")
        self.assertIn("tasks", response.context)
        self.assertIn("form", response.context)
        self.assertIn("app_version", response.context)

    def test_update_task_get(self):
        url = reverse("update_task", args=[self.task.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/update_task.html")
        self.assertIn("form", response.context)

    def test_update_task_post_valid(self):
        url = reverse("update_task", args=[self.task.id])
        payload = {
            "title": "Updated title",
            "complete": True,
        }

        response = self.client.post(url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")

        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated title")
        self.assertTrue(self.task.complete)

    def test_update_task_post_invalid(self):
        url = reverse("update_task", args=[self.task.id])
        old_title = self.task.title

        payload = {
            "title": "", 
            "complete": False,
        }

        response = self.client.post(url, data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/update_task.html")

        self.task.refresh_from_db()
        self.assertEqual(self.task.title, old_title)


    def test_delete_task_get(self):
        url = reverse("delete", args=[self.task.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/delete.html")
        self.assertIn("item", response.context)

    def test_delete_task_post(self):
        url = reverse("delete", args=[self.task.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")

        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

class TestDatasetImport(TestCase):
    def test_import_tasks_from_dataset_populates_db(self):
        self.assertEqual(Task.objects.count(), 0)

        import_tasks_from_dataset()

        dataset_path = Path(__file__).resolve().parent / "dataset.json"
        with dataset_path.open(encoding="utf-8") as f:
            data = json.load(f)

        expected_titles = {item["title"] for item in data}
        titles_in_db = set(Task.objects.values_list("title", flat=True))

        self.assertTrue(
            expected_titles.issubset(titles_in_db),
            msg=f"Les titres attendus {expected_titles} ne sont pas tous en base {titles_in_db}",
        )
