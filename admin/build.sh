#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="kikis-kitchen-admin"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# Project root = parent
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd -P)"

DIST_DIR="$PROJECT_ROOT/docker_dist"

BASE_TAG="python:3.11-slim"
BASE_TAR_NAME="python_3.11-slim__linux_amd64__2026-02-06.tar"
BASE_TAR="$DIST_DIR/$BASE_TAR_NAME"

PROJECT_NAME="$(basename "$PROJECT_ROOT")"

echo "📦 Project root:   $PROJECT_NAME"
echo "📦 Dist dir:        $DIST_DIR"
echo "🐍 Base image tag:  $BASE_TAG"
echo "📄 Base tarball:    $BASE_TAR"

# Load base image only if missing
if docker image inspect "$BASE_TAG" >/dev/null 2>&1; then
  echo "✅ Base image already present: $BASE_TAG"
else
  if [[ ! -f "$BASE_TAR" ]]; then
    echo "❌ Missing base tarball: $BASE_TAR"
    echo "   Create it once with:"
    echo "     docker pull --platform=linux/amd64 python:3.11-slim"
    echo "     docker save python:3.11-slim -o \"$BASE_TAR\""
    exit 1
  fi
  echo "📦 Loading base image from: $BASE_TAR"
  docker load -i "$BASE_TAR"
fi

echo "Building image: ${IMAGE_NAME}"
docker build -t "${IMAGE_NAME}" .
echo "Done."