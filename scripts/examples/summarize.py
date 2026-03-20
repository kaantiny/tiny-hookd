#!/usr/bin/env python3
"""
Webhook: Summarize any text with AI
POST /examples/summarize.py
Body: { "text": "long article here...", "style": "bullet" }

Styles: brief | bullet | eli5 | tweet
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib.llm import ask

STYLES = {
    "brief":  "Summarize in 2-3 sentences:",
    "bullet": "Summarize as bullet points (max 5):",
    "eli5":   "Explain like I'm 5:",
    "tweet":  "Summarize in a single tweet (max 280 chars):",
}

payload = json.loads(sys.stdin.read())
text = payload.get("text", "")
style = payload.get("style", "brief")

result = ask(text, system=STYLES.get(style, STYLES["brief"]))
print(json.dumps({"summary": result, "style": style}))
