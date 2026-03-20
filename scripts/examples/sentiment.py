#!/usr/bin/env python3
"""
Webhook: Analyze sentiment of text
POST /examples/sentiment.py
Body: { "text": "I love this product! Best purchase ever." }
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib.llm import ask_json

payload = json.loads(sys.stdin.read())
text = payload.get("text", "")

result = ask_json(
    f"Analyze the sentiment of this text:\n\n{text}",
    system="Return JSON: sentiment (positive/negative/neutral), confidence (0-1), emotions (array), summary (one sentence).",
    temperature=0.2,
)

print(json.dumps(result, indent=2))
