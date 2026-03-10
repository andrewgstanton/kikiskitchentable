#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="${CONTAINER_NAME:-kikis-kitchen-admin}"
PORT="${PORT:-7000}"

echo "Stopping container ${CONTAINER_NAME} if present..."
docker stop "${CONTAINER_NAME}" 2>/dev/null || true
docker rm "${CONTAINER_NAME}" 2>/dev/null || true

echo "Looking for any other Docker containers using port ${PORT}..."
CONTAINER_IDS="$(docker ps -q --filter "publish=${PORT}")"

if [ -n "${CONTAINER_IDS}" ]; then
  echo "Stopping containers using port ${PORT}: ${CONTAINER_IDS}"
  docker stop ${CONTAINER_IDS} || true
  docker rm ${CONTAINER_IDS} || true
fi

echo "Done."