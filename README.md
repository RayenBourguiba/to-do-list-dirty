# to-do-list app
To-Do-List application built with django to Create, Update and Delete tasks.
<br>
<br>
![todolist](https://user-images.githubusercontent.com/65074901/125083144-a5e03900-e0e5-11eb-9092-da716a30a5f3.JPG)

## Stratégie de versions & commits

Nous utilisons :

- **SemVer** (`MAJEUR.MINOR.PATCH`) pour les versions :
  - MAJEUR : changements incompatibles (ex : 2.0.0)
  - MINOR : nouvelles fonctionnalités rétro-compatibles (ex : 1.1.0)
  - PATCH : corrections de bugs (ex : 1.0.1)

- **Conventional Commits** pour les messages de commit :
  - `feat: description` → nouvelle fonctionnalité
  - `fix: description` → correction de bug
  - `chore: description` → tâches techniques (build, dépendances, etc.)
  - `docs: description` → documentation

Exemples :

- `feat: afficher la version sur la page d'accueil`
- `fix: corriger le bug de suppression de tâche`
- `chore(release): 1.1.0`

Les versions sont taguées dans Git (`git tag 1.1.0`), et une archive ZIP est générée via le script `build.sh` ou `build.ps1`.

## Matrice de tests (Python / Django)
Les tests automatiques peuvent être lancés sur plusieurs versions de Python et de Django
grâce au script `test_matrix.sh`.

Ce script utilise `pipenv` pour créer des environnements isolés pour chaque
combinaison (Python 3.13 / 3.9 avec Django 5 / 4.2 / 3.2), installe les dépendances
et exécute `python manage.py test tasks` pour chaque cas.