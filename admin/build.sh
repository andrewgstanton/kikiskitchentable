#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="kikis-kitchen-admin"

echo "Building image: ${IMAGE_NAME}"
docker build -t "${IMAGE_NAME}" .
echo "Done."