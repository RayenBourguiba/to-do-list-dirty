import json
from pathlib import Path

from django.test import TestCase
from django.urls import reverse

from tasks.models import Task
from tasks.utils import import_tasks_from_dataset


class TestTaskViews(TestCase):
    def setUp(self):
        self.task = Task.objects.create(
            title="Test task",
            complete=False,
        )

    def test_home_page_post_creates_task(self):
        url = reverse("list")
        payload = {"title": "Created via POST"}

        response = self.client.post(url, data=payload)

        # Redirection vers la home
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")

        # La tâche est bien créée
        self.assertTrue(Task.objects.filter(title="Created via POST").exists())

    def test_home_page_post_invalid_does_not_create_task(self):
        """
        POST / avec un titre vide ne doit pas créer de tâche.
        On garde le comportement de redirection.
        """
        url = reverse("list")
        initial_count = Task.objects.count()

        payload = {"title": ""}

        response = self.client.post(url, data=payload)

        # Toujours une redirection
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")

        # Aucune tâche supplémentaire
        self.assertEqual(Task.objects.count(), initial_count)

    def test_home_page_get(self):
        """
        GET / doit renvoyer 200.
        On ne s'appuie pas sur response.context dans ce runner custom.
        """
        url = reverse("list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        # On vérifie juste qu'il y a bien du HTML renvoyé
        html = response.content.decode("utf-8")
        self.assertGreater(len(html), 0)

    def test_update_task_get(self):
        """
        GET /update_task/<id>/ doit renvoyer 200.
        On vérifie que le titre de la tâche apparaît dans la page (valeur du champ).
        """
        url = reverse("update_task", args=[self.task.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")
        self.assertIn(self.task.title, html)

    def test_update_task_post_valid(self):
        url = reverse("update_task", args=[self.task.id])
        payload = {
            "title": "Updated title",
            "complete": True,
        }

        response = self.client.post(url, data=payload)

        # Redirection après mise à jour
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")

        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated title")
        self.assertTrue(self.task.complete)

    def test_update_task_post_invalid(self):
        """
        POST /update_task/<id>/ avec un titre vide doit réafficher le formulaire
        sans modifier la tâche.
        """
        url = reverse("update_task", args=[self.task.id])
        old_title = self.task.title

        payload = {"title": "", "complete": False}

        response = self.client.post(url, data=payload)

        # Pas de redirection : on reste sur la page du formulaire
        self.assertEqual(response.status_code, 200)

        # La tâche n'a pas été modifiée
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, old_title)

    def test_delete_task_get(self):
        """
        GET /delete/<id>/ doit afficher la page de confirmation.
        On vérifie le status et la présence du titre de la tâche.
        """
        url = reverse("delete", args=[self.task.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")
        self.assertIn(self.task.title, html)

    def test_delete_task_post(self):
        url = reverse("delete", args=[self.task.id])
        response = self.client.post(url)

        # Redirection après suppression
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")

        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_delete_task_post_does_not_delete_other_tasks(self):
        """
        La suppression d'une tâche ne doit pas supprimer les autres tâches.
        """
        other_task = Task.objects.create(
            title="Other task",
            complete=False,
        )

        url = reverse("delete", args=[self.task.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(id=other_task.id).exists())

    def test_home_page_displays_existing_task(self):
        """
        La page d'accueil doit afficher le titre de la tâche créée en setUp.
        """
        url = reverse("list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")
        self.assertIn(self.task.title, html)

    def test_completed_task_rendered_with_css_class(self):
        """
        Une tâche complete=True doit être rendue avec la classe CSS 'task-complete'.
        """
        self.task.complete = True
        self.task.save()

        url = reverse("list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")
        self.assertIn("task-complete", html)

    def test_home_page_post_creates_incomplete_task_by_default(self):
        """
        Une tâche créée sans cocher 'complete' doit être (False) par défaut.
        """
        url = reverse("list")
        payload = {"title": "Task without checkbox"}

        self.client.post(url, data=payload)

        task = Task.objects.get(title="Task without checkbox")
        self.assertFalse(task.complete)

    def test_home_page_post_strips_whitespace_in_title(self):
        """
        Le formulaire doit supprimer les espaces inutiles autour du titre.
        """
        url = reverse("list")
        payload = {"title": "   Trimmed title   "}

        self.client.post(url, data=payload)

        self.assertTrue(Task.objects.filter(title="Trimmed title").exists())


class TestDatasetImport(TestCase):
    def test_import_tasks_from_dataset_populates_db(self):
        """
        La fonction import_tasks_from_dataset() doit insérer les tâches du dataset
        dans la base.
        """
        self.assertEqual(Task.objects.count(), 0)

        import_tasks_from_dataset()

        dataset_path = Path(__file__).resolve().parent / "dataset.json"
        with dataset_path.open(encoding="utf-8") as f:
            data = json.load(f)

        expected_titles = {item["title"] for item in data}
        titles_in_db = set(Task.objects.values_list("title", flat=True))

        self.assertTrue(
            expected_titles.issubset(titles_in_db),
            msg=(
                f"Les titres attendus {expected_titles} "
                f"ne sont pas tous en base {titles_in_db}"
            ),
        )


class TestTaskModel(TestCase):
    def test_task_str_returns_title(self):
        """
        La représentation en chaîne d'une tâche doit renvoyer son titre.
        """
        task = Task.objects.create(title="My title", complete=False)
        self.assertEqual(str(task), "My title")
