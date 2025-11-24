from django.test import TestCase
from django.urls import reverse
from tasks.models import Task


class TestTaskViews(TestCase):
    def setUp(self):
        self.task = Task.objects.create(
            title="Test task",
            complete=False,
        )

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
