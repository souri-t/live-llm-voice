#!/bin/sh
set -eu
gateway_url="${GATEWAY_URL:-http://localhost:8000}"
curl --fail --silent --show-error "$gateway_url/health"
echo
echo "Gateway health check passed. Complete the voice round-trip in Chrome using docs/verification.md."
