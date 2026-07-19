#!/bin/sh
set -eu
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
[ -f "$project_dir/.env" ] || cp "$project_dir/.env.example" "$project_dir/.env"
[ -f "$project_dir/frontend/.env" ] || cp "$project_dir/frontend/.env.example" "$project_dir/frontend/.env"
(cd "$project_dir/gateway" && uv sync)
(cd "$project_dir/frontend" && npm install)
echo "Setup complete. Add LLM_API_KEY and LLM_MODEL to .env."
