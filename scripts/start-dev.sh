#!/bin/sh
set -eu
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if [ ! -f "$project_dir/.env" ]; then echo "Run ./scripts/setup.sh first." >&2; exit 1; fi
(cd "$project_dir" && docker compose up --build -d)
echo "Gateway is starting. Run 'cd frontend && npm run dev' in another terminal."
