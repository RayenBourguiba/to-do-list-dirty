#!/usr/bin/env bash
set -e

pipenv run python manage.py shell -c "from tasks.utils import import_tasks_from_dataset; import_tasks_from_dataset()"
pipenv run python manage.py runserver 8000 &
SERVER_PID=$!

sleep 5

echo "Running pa11y accessibility checks..."

npx pa11y http://127.0.0.1:8000 \
  --standard WCAG2A \
  --threshold 0

npx pa11y http://127.0.0.1:8000/update_task/1 --standard WCAG2A --threshold 0
npx pa11y http://127.0.0.1:8000/delete/1 --standard WCAG2A --threshold 0

echo "pa11y checks passed (0 issues)."

kill "$SERVER_PID" || true
wait "$SERVER_PID" 2>/dev/null || true
