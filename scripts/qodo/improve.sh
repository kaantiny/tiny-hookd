#!/bin/bash
# ============================================================
# Webhook: Trigger Qodo Merge code improvement suggestions
# POST /qodo/improve.sh
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

echo "Running Qodo improve on: $PR_URL" >&2

qodo-merge --pr_url "$PR_URL" improve 2>&1

echo "{\"status\": \"ok\", \"action\": \"improve\", \"pr_url\": \"$PR_URL\"}"
