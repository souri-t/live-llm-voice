#!/bin/sh
set -eu
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
(cd "$project_dir/gateway" && uv run pytest)
(cd "$project_dir/frontend" && npm test && npm run build)
(cd "$project_dir" && docker compose --env-file .env.example config --quiet)
(cd "$project_dir" && docker compose --env-file .env.example build whisper)
docker run --rm --entrypoint whisper-server livellm-whisper:latest --help >/dev/null 2>&1
