#!/usr/bin/env python3
"""
Webhook: AI code review
POST /examples/code-review.py
Body: { "code": "def foo(x): return x+1", "language": "python" }
"""
import sys
import json
sys.path.insert(0, "/var/opt/webhookd/scripts")
from lib.llm import ask_json

payload = json.loads(sys.stdin.read())
code = payload.get("code", "")
lang = payload.get("language", "auto-detect")

result = ask_json(
    f"Review this {lang} code:\n\n```\n{code}\n```",
    system="""You are a senior code reviewer. Return JSON with:
- score (1-10)
- issues (array of {severity: "high"|"medium"|"low", line: number or null, message: string})
- suggestions (array of improvement strings)
- summary (one paragraph review)""",
    temperature=0.3,
)

print(json.dumps(result, indent=2))
