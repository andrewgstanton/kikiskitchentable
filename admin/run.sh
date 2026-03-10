#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="kikis-kitchen-admin"
CONTAINER_NAME="kikis-kitchen-admin"
PORT="${PORT:-7000}"

REPO_ROOT="$(cd .. && pwd)"

echo "Starting container ${CONTAINER_NAME}..."

# remove any previous container with same name
docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true

docker run --rm \
  --name "${CONTAINER_NAME}" \
  -p "${PORT}:${PORT}" \
  -e PORT="${PORT}" \
  -v "${REPO_ROOT}":/workspace \
  -w /workspace/admin \
  "${IMAGE_NAME}"