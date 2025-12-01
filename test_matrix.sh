#!/usr/bin/env bash
set -e

PYTHONS=("3.13" "3.9" "2.7")
DJANGOS=("5.0" "4.2" "3.2")

for PY_VERSION in "${PYTHONS[@]}"; do
  echo "========================================="
  echo "Tests pour Python ${PY_VERSION}"
  echo "========================================="

  PIPENV_PYTHON="python${PY_VERSION}"
  export PIPENV_PYTHON

  pipenv --rm 2>/dev/null || true
  pipenv --python "${PIPENV_PYTHON}"

  for DJ_VERSION in "${DJANGOS[@]}"; do
    if [ "$PY_VERSION" = "3.13" ] && [ "$DJ_VERSION" = "3.2" ]; then
        echo "On saute Python ${PY_VERSION} + Django ${DJ_VERSION} (combinaison non supportée : distutils manquant)"
    continue
    fi

    echo "-----------------------------------------"
    echo "Python ${PY_VERSION} + Django ${DJ_VERSION}"
    echo "-----------------------------------------"

    pipenv install "django==${DJ_VERSION}"
    pipenv install --dev ruff coverage

    pipenv run python manage.py test tasks || {
      echo "Échec pour Python ${PY_VERSION} + Django ${DJ_VERSION}"
      exit 1
    }

    echo "Succès pour Python ${PY_VERSION} + Django ${DJ_VERSION}"
  done
done

echo "Tous les tests sont passés pour toutes les combinaisons valides."
