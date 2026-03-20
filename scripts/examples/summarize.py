#!/usr/bin/env python3
"""
Webhook: Summarize any text with AI
POST /examples/summarize.py
Body: { "text": "long article here...", "style": "bullet" }
"""
import sys
import json
sys.path.insert(0, "/var/opt/webhookd/scripts")
from lib.llm import ask

payload = json.loads(sys.stdin.read())
text = payload.get("text", "")
style = payload.get("style", "brief")  # brief | bullet | eli5 | tweet

prompts = {
    "brief": "Summarize in 2-3 sentences:",
    "bullet": "Summarize as bullet points (max 5):",
    "eli5": "Explain like I'm 5:",
    "tweet": "Summarize in a single tweet (max 280 chars):",
}

system = prompts.get(style, prompts["brief"])
result = ask(text, system=system)

print(json.dumps({"summary": result, "style": style}))
