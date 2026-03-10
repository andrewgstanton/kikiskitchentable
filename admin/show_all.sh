#!/usr/bin/env bash
set -euo pipefail

docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Ports}}"