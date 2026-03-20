#!/bin/bash
# ============================================================
# Webhook: Run full Qodo suite (describe + review + improve)
# POST /qodo/full-suite.sh
# Body: { "pr_url": "https://github.com/owner/repo/pull/123" }
# ============================================================

set -euo pipefail

PAYLOAD=$(cat)

PR_URL=$(echo "$PAYLOAD" | jq -r '
  if .pull_request.html_url then .pull_request.html_url
  elif .pr_url then .pr_url
  else empty
  end
' 2>/dev/null)

if [ -z "$PR_URL" ]; then
  echo '{"error": "No PR URL found."}'
  exit 1
fi

echo "Running full Qodo suite on: $PR_URL" >&2

echo "→ describe..." >&2
qodo-merge --pr_url "$PR_URL" describe 2>&1 || true

echo "→ review..." >&2
qodo-merge --pr_url "$PR_URL" review 2>&1 || true

echo "→ improve..." >&2
qodo-merge --pr_url "$PR_URL" improve 2>&1 || true

echo "{\"status\": \"ok\", \"action\": \"full-suite\", \"steps\": [\"describe\", \"review\", \"improve\"], \"pr_url\": \"$PR_URL\"}"
