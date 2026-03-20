#!/usr/bin/env python3
"""
Webhook: GitHub PR event router for Qodo
POST /qodo/github-webhook.py

Point your GitHub repo webhook here with pull_request events.
Auto-triggers Qodo actions:
  - PR opened      → describe + review
  - PR synchronize → review (new commits pushed)
  - PR reopened    → review

Env vars required:
  OPENAI_API_KEY   - For Qodo LLM calls
  GITHUB_TOKEN     - GitHub PAT with repo access
"""

import sys
import os
import json
import subprocess


def run_qodo(pr_url: str, command: str) -> dict:
    """Run a qodo-merge CLI command."""
    result = subprocess.run(
        ["qodo-merge", "--pr_url", pr_url, command],
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ},
    )
    return {
        "command": command,
        "exit_code": result.returncode,
        "stdout": result.stdout[-500:] if result.stdout else "",
        "stderr": result.stderr[-500:] if result.stderr else "",
    }


def main():
    payload_raw = sys.stdin.read()

    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON payload"}))
        return

    action = payload.get("action", "")
    pr = payload.get("pull_request", {})
    pr_url = pr.get("html_url", "")

    if not pr_url:
        print(json.dumps({"status": "skipped", "reason": "Not a pull_request event"}))
        return

    if pr.get("draft", False):
        print(json.dumps({"status": "skipped", "reason": "Draft PR"}))
        return

    results = []

    if action == "opened":
        print(f"New PR opened: {pr_url}", file=sys.stderr)
        results.append(run_qodo(pr_url, "describe"))
        results.append(run_qodo(pr_url, "review"))

    elif action == "synchronize":
        print(f"PR updated: {pr_url}", file=sys.stderr)
        results.append(run_qodo(pr_url, "review"))

    elif action == "reopened":
        print(f"PR reopened: {pr_url}", file=sys.stderr)
        results.append(run_qodo(pr_url, "review"))

    else:
        print(json.dumps({"status": "skipped", "reason": f"Unhandled action: {action}"}))
        return

    print(json.dumps({
        "status": "ok",
        "pr_url": pr_url,
        "action": action,
        "results": results,
    }, indent=2))


if __name__ == "__main__":
    main()
