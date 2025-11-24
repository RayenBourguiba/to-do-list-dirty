#!/usr/bin/env bash
set -e

if [ -z "$1" ]; then
  echo "Usage: ./build.sh version=1.0.1"
  exit 1
fi

VERSION="${1#version=}"

if [ -z "$VERSION" ]; then
  echo "Version invalide. Utilise: ./build.sh version=1.0.1"
  exit 1
fi

echo "🔧 Build pour la version $VERSION"

SETTINGS_FILE="todo/settings.py"

sed -i "s/^APP_VERSION = \".*\"/APP_VERSION = \"$VERSION\"/" "$SETTINGS_FILE"

git add "$SETTINGS_FILE"
git commit -m "chore(release): $VERSION"

git tag "$VERSION"

git archive --format=zip "$VERSION" -o "todolist-$VERSION.zip"

echo "Build terminé : todolist-$VERSION.zip"
