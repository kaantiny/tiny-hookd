#!/usr/bin/env python3
"""
Webhook: GitHub PR event router for Qodo
POST /qodo/github-webhook.py

This is designed to be your GitHub webhook receiver.
Set your GitHub repo webhook URL to: http://your-server:8080/qodo/github-webhook.py

It listens for pull_request events and auto-triggers Qodo actions:
  - PR opened      → describe + review
  - PR synchronize → review (new commits pushed)
  - PR reopened    → review

Env vars required:
  OPENAI_API_KEY   - For Qodo/PR-Agent LLM calls
  GITHUB_TOKEN     - GitHub PAT with repo access
  WEBHOOK_SECRET   - (optional) GitHub webhook secret for signature verification
"""

import sys
import os
import json
import subprocess
import hmac
import hashlib

def verify_signature(payload_body: str, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature (X-Hub-Signature-256)."""
    if not secret:
        return True  # Skip if no secret configured
    expected = "sha256=" + hmac.new(secret.encode(), payload_body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def run_qodo(pr_url: str, command: str) -> dict:
    """Run a Qodo PR-Agent command via Docker."""
    result = subprocess.run(
        [
            "docker", "run", "--rm",
            "-e", f"OPENAI_KEY={os.getenv('OPENAI_API_KEY', '')}",
            "-e", f"GITHUB_TOKEN={os.getenv('GITHUB_TOKEN', '')}",
            "-e", "CONFIG.GIT_PROVIDER=github",
            "codiumai/pr-agent:latest",
            "--pr_url", pr_url,
            command,
        ],
        capture_output=True,
        text=True,
        timeout=300,
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

    # Check if it's a pull_request event
    action = payload.get("action", "")
    pr = payload.get("pull_request", {})
    pr_url = pr.get("html_url", "")

    if not pr_url:
        print(json.dumps({"status": "skipped", "reason": "Not a pull_request event"}))
        return

    # Skip draft PRs
    if pr.get("draft", False):
        print(json.dumps({"status": "skipped", "reason": "Draft PR"}))
        return

    # Route based on action
    results = []

    if action == "opened":
        # New PR → full treatment
        print(f"New PR opened: {pr_url}", file=sys.stderr)
        results.append(run_qodo(pr_url, "describe"))
        results.append(run_qodo(pr_url, "review"))

    elif action == "synchronize":
        # New commits pushed → re-review
        print(f"PR updated: {pr_url}", file=sys.stderr)
        results.append(run_qodo(pr_url, "review"))

    elif action == "reopened":
        # PR reopened → review
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
