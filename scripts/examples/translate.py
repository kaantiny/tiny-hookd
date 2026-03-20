#!/usr/bin/env python3
"""
Webhook: Translate text to any language
POST /examples/translate.py
Body: { "text": "Hello world", "to": "Vietnamese" }
"""
import sys
import json
from tiny_hookd import ask

payload = json.loads(sys.stdin.read())
text = payload.get("text", "")
target = payload.get("to", "English")

result = ask(
    text,
    system=f"Translate the following to {target}. Only output the translation, nothing else.",
    temperature=0.3,
)

print(json.dumps({"original": text, "translated": result, "language": target}))
