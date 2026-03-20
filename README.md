# tiny-hookd 🪝

Battery-included [webhookd](https://github.com/ncarlier/webhookd) Docker image with **Python**, **Qodo Merge**, and **GitHub CLI** baked in.

Drop a script → get an HTTP endpoint. That's it.

## What's Inside

| Layer | Included |
|-------|----------|
| **webhookd** | Latest release — turns scripts into webhooks |
| **Python 3.11** | openai, anthropic, tenacity, requests, httpx, pydantic, rich |
| **tiny_hookd** | System-installed Python package — `from tiny_hookd import ask` anywhere |
| **llm-ask** | CLI tool — call the LLM from bash scripts |
| **Qodo Merge** | `qodo-merge` CLI — AI code review for PRs |
| **GitHub CLI** | `gh` — interact with GitHub from scripts |

## Quick Start

```bash
git clone https://github.com/kaantiny/tiny-hookd.git
cd tiny-hookd
cp .env.example .env     # add your OPENAI_API_KEY + GITHUB_TOKEN
docker compose up --build
```

Then open:
- **Webhooks:** http://localhost:8080
- **Script Editor:** http://localhost:8081 (default login: `admin` / `admin`)

Test it:
```bash
curl http://localhost:8080/examples/hello.sh
```

## Project Structure

```
lib/                          # Python package (installed system-wide in Docker)
├── pyproject.toml
└── tiny_hookd/
    ├── __init__.py
    ├── llm.py                # ask, chat, stream, ask_json, embed
    └── cli.py                # llm-ask CLI entrypoint

scripts/
├── examples/
│   ├── hello.sh              # Health check
│   ├── ask-llm.sh            # Bash → LLM via llm-ask CLI
│   ├── summarize.py          # AI text summarization
│   ├── translate.py          # AI translation
│   ├── sentiment.py          # Sentiment analysis
│   └── extract.py            # Structured data extraction
└── qodo/
    ├── review.sh             # Qodo code review on a PR
    ├── improve.sh            # Qodo improvement suggestions
    ├── describe.sh            # Auto-generate PR description
    ├── full-suite.sh         # Run all 3 sequentially
    └── github-webhook.py     # Auto-router for GitHub PR events
```

## LLM Library

Installed system-wide as `tiny_hookd` — no path hacks, just import:

### From Python (anywhere)

```python
from tiny_hookd import ask, ask_json, chat, stream, embed

answer = ask("What is Docker?")
answer = ask("Summarize this", system="Be concise", model="gpt-4o")
data = ask_json("List 3 colors as JSON")

for chunk in stream("Tell me a story"):
    print(chunk, end="")
```

### From Bash (via `llm-ask` CLI)

```bash
# Simple question
llm-ask "What is Docker?"

# With system prompt
llm-ask --system "Be concise" "Explain Kubernetes"

# Pipe input
echo "Long text here..." | llm-ask --system "Summarize in 1 sentence"

# JSON output
llm-ask --json "List 3 colors"

# Model override
llm-ask --model gpt-4o "Complex question"
```

Both include automatic retry with exponential backoff on 429 / 5xx errors.

## Qodo PR Review

Trigger AI code review on any GitHub PR:

```bash
# Single review
curl -X POST http://localhost:8080/qodo/review.sh \
  -d '{"pr_url": "https://github.com/owner/repo/pull/1"}'

# Full suite (describe + review + improve)
curl -X POST http://localhost:8080/qodo/full-suite.sh \
  -d '{"pr_url": "https://github.com/owner/repo/pull/1"}'
```

**Auto-review:** Point a GitHub webhook (pull_request events) at `/qodo/github-webhook.py` to auto-review on PR open and re-review on push.

## Script Editor (Filebrowser)

The stack includes [Filebrowser](https://filebrowser.org) at `:8081` — a clean web UI to browse, edit, and create scripts directly in the browser.

A `chmod-watcher` sidecar automatically makes any `.sh`, `.py`, or `.bash` file executable when created or modified, so scripts saved through the editor are immediately runnable by webhookd.

Default credentials: `admin` / `admin` (change on first login).

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key (used by LLM lib + Qodo) |
| `GITHUB_TOKEN` | For Qodo | GitHub PAT with `repo` scope |
| `LLM_BASE_URL` | No | Custom base URL (proxies, local LLMs) |
| `LLM_MODEL` | No | Default model (default: `gpt-4o-mini`) |
| `EDITOR_PORT` | No | Filebrowser port (default: `8081`) |

## License

MIT
