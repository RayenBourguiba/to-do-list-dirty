from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings

from .models import Task
from .forms import TaskForm


def index(request):
    """
    Page d'accueil :
    - GET  -> 200 + render("tasks/list.html", ...)
    - POST -> tente de créer une tâche puis redirige toujours vers "list"
    """
    tasks = Task.objects.all().order_by("id")

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
        # Toujours rediriger après un POST (même si le form est invalide)
        return redirect("list")

    # GET
    form = TaskForm()
    context = {
        "tasks": tasks,
        "form": form,
        "app_version": getattr(settings, "APP_VERSION", "1.2.0"),
    }
    return render(request, "tasks/list.html", context)


def updateTask(request, pk):
    """
    - GET  : 200 + template "tasks/update_task.html"
    - POST valide   : 302 vers "list"
    - POST invalide : 200 + même template réaffiché
    """
    task = get_object_or_404(Task, id=pk)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("list")
        # form invalide => on retombe sur le render plus bas
    else:
        form = TaskForm(instance=task)

    context = {"form": form}
    return render(request, "tasks/update_task.html", context)


def deleteTask(request, pk):
    """
    - GET  : 200 + template "tasks/delete.html" (context: item)
    - POST : supprime + 302 vers "list"
    """
    task = get_object_or_404(Task, id=pk)

    if request.method == "POST":
        task.delete()
        return redirect("list")

    context = {"item": task}
    return render(request, "tasks/delete.html", context)
