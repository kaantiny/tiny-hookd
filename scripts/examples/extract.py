#!/usr/bin/env python3
"""
Webhook: Extract structured data from unstructured text
POST /examples/extract.py
Body: { "text": "Call me at 555-1234, my email is john@example.com", "fields": ["name", "phone", "email"] }
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib.llm import ask_json

payload = json.loads(sys.stdin.read())
text = payload.get("text", "")
fields = payload.get("fields", ["name", "email", "phone", "date", "address"])
fields_str = ", ".join(fields)

result = ask_json(
    f"Extract the following fields from this text: {fields_str}\n\nText:\n{text}",
    system=f"Extract structured data. Return JSON with keys: {fields_str}. Use null for fields not found.",
    temperature=0.1,
)

print(json.dumps(result, indent=2))
