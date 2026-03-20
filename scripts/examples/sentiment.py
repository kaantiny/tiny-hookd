#!/usr/bin/env python3
"""
Webhook: Analyze sentiment of text
POST /examples/sentiment.py
Body: { "text": "I love this product! Best purchase ever." }
"""
import sys
import json
sys.path.insert(0, "/var/opt/webhookd/scripts")
from lib.llm import ask_json

payload = json.loads(sys.stdin.read())
text = payload.get("text", "")

result = ask_json(
    f"Analyze the sentiment of this text:\n\n{text}",
    system="Return JSON with: sentiment (positive/negative/neutral), confidence (0-1), emotions (array of detected emotions), summary (one sentence explanation).",
    temperature=0.2,
)

print(json.dumps(result, indent=2))
