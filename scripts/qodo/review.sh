#!/bin/bash
# ============================================================
# Webhook: Trigger Qodo Merge (PR-Agent) code review on a PR
# POST /qodo/review.sh
# Body: GitHub webhook payload (pull_request event)
#       OR manual: { "pr_url": "https://github.com/owner/repo/pull/123" }
#
# Runs: /review (full code review with inline comments)
# ============================================================

set -euo pipefail

PAYLOAD=$(cat)

# Extract PR URL from GitHub webhook or manual payload
PR_URL=$(echo "$PAYLOAD" | jq -r '
  if .pull_request.html_url then .pull_request.html_url
  elif .pr_url then .pr_url
  else empty
  end
' 2>/dev/null)

if [ -z "$PR_URL" ]; then
  echo '{"error": "No PR URL found. Send GitHub PR webhook or {\"pr_url\": \"...\"}"}'
  exit 1
fi

echo "Running Qodo review on: $PR_URL" >&2

# Run PR-Agent via Docker
docker run --rm \
  -e OPENAI_KEY="${OPENAI_API_KEY}" \
  -e GITHUB_TOKEN="${GITHUB_TOKEN}" \
  -e CONFIG.GIT_PROVIDER="github" \
  codiumai/pr-agent:latest \
  --pr_url "$PR_URL" \
  review

echo "{\"status\": \"ok\", \"action\": \"review\", \"pr_url\": \"$PR_URL\"}"
