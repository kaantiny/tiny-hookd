#!/usr/bin/env python3
"""
llm-ask — Quick CLI to call the LLM from bash scripts.

Usage:
    echo "What is Docker?" | llm-ask
    llm-ask "What is Docker?"
    llm-ask --system "Be concise" "Explain Kubernetes"
    llm-ask --json "List 3 colors as JSON"
    llm-ask --model gpt-4o "Complex question"
"""

import argparse
import sys
import json
from tiny_hookd import ask, ask_json


def main():
    parser = argparse.ArgumentParser(description="Ask the LLM from the command line")
    parser.add_argument("prompt", nargs="?", default=None, help="Prompt text (or pipe via stdin)")
    parser.add_argument("-s", "--system", default=None, help="System prompt")
    parser.add_argument("-m", "--model", default=None, help="Model override")
    parser.add_argument("-t", "--temperature", type=float, default=None, help="Temperature")
    parser.add_argument("--json", action="store_true", help="Return JSON (json_object mode)")
    parser.add_argument("--raw", action="store_true", help="Output raw text, no trailing newline")
    args = parser.parse_args()

    # Get prompt from args or stdin
    prompt = args.prompt
    if not prompt:
        if not sys.stdin.isatty():
            prompt = sys.stdin.read().strip()
        else:
            parser.error("Provide a prompt as argument or via stdin")

    if args.json:
        result = ask_json(prompt, system=args.system, model=args.model)
        print(json.dumps(result, indent=2))
    else:
        result = ask(prompt, system=args.system, model=args.model, temperature=args.temperature)
        if args.raw:
            print(result, end="")
        else:
            print(result)


if __name__ == "__main__":
    main()
