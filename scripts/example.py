#!/usr/bin/env python3
"""
Example Python webhook script with OpenAI + retry
Receives JSON payload via stdin
"""
import sys
import json
import os
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

# Load API key from env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def process_with_ai(text: str) -> str:
    """Example: Process text with OpenAI (with retry)"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Summarize: {text}"}]
    )
    return response.choices[0].message.content

def main():
    # Read payload from stdin
    payload = sys.stdin.read()
    
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        data = {"raw": payload}
    
    print(json.dumps({
        "status": "ok",
        "received_at": str(__import__('datetime').datetime.now()),
        "data": data,
        "message": "Webhook processed successfully"
    }, indent=2))

if __name__ == "__main__":
    main()
