#!/bin/bash
# ============================================================
# Webhook: Run full Qodo suite (describe + review + improve)
# POST /qodo/full-suite.sh
# Body: { "pr_url": "https://github.com/owner/repo/pull/123" }
#
# Runs all 3 commands sequentially on a PR
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

DOCKER_OPTS="-e OPENAI_KEY=${OPENAI_API_KEY} -e GITHUB_TOKEN=${GITHUB_TOKEN} -e CONFIG.GIT_PROVIDER=github"
IMAGE="codiumai/pr-agent:latest"

echo "Running full Qodo suite on: $PR_URL" >&2

# 1. Describe
echo "→ Running describe..." >&2
docker run --rm $DOCKER_OPTS $IMAGE --pr_url "$PR_URL" describe 2>&1 || true

# 2. Review
echo "→ Running review..." >&2
docker run --rm $DOCKER_OPTS $IMAGE --pr_url "$PR_URL" review 2>&1 || true

# 3. Improve
echo "→ Running improve..." >&2
docker run --rm $DOCKER_OPTS $IMAGE --pr_url "$PR_URL" improve 2>&1 || true

echo "{\"status\": \"ok\", \"action\": \"full-suite\", \"steps\": [\"describe\", \"review\", \"improve\"], \"pr_url\": \"$PR_URL\"}"
