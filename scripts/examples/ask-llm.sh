#!/bin/bash
# ============================================================
# Webhook: Ask the LLM from bash (showcases llm-ask CLI)
# POST /examples/ask-llm.sh
# Body: { "prompt": "What is Docker?", "system": "Be concise" }
# ============================================================

set -euo pipefail

PAYLOAD=$(cat)
PROMPT=$(echo "$PAYLOAD" | jq -r '.prompt // empty')
SYSTEM=$(echo "$PAYLOAD" | jq -r '.system // empty')

if [ -z "$PROMPT" ]; then
  echo '{"error": "Missing prompt field"}'
  exit 1
fi

if [ -n "$SYSTEM" ]; then
  RESULT=$(echo "$PROMPT" | llm-ask --system "$SYSTEM" --raw)
else
  RESULT=$(echo "$PROMPT" | llm-ask --raw)
fi

# Output as JSON
jq -n --arg result "$RESULT" '{"result": $result}'
