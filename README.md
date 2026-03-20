# tiny-hookd 🪝

Battery-included [webhookd](https://github.com/ncarlier/webhookd) Docker image with **Node.js**, **Python**, **LLM libs**, **Qodo Merge** (PR-Agent), and **GitHub CLI** baked in.

Drop a script → get an HTTP endpoint. That's it.

## What's Inside

| Layer | Included |
|-------|----------|
| **webhookd** | Latest release — turns scripts into webhooks |
| **Node.js 20** | openai, @anthropic-ai/sdk, p-retry, axios, typescript |
| **Python 3.11** | openai, anthropic, tenacity, requests, httpx, pydantic |
| **Qodo Merge** | `qodo-merge` CLI — AI code review for PRs |
| **GitHub CLI** | `gh` — interact with GitHub from scripts |
| **LLM wrapper** | `scripts/lib/llm.py` + `llm.js` — zero-config `ask()` / `chat()` / `stream()` |

## Quick Start

```bash
git clone https://github.com/kaantiny/tiny-hookd.git
cd tiny-hookd
cp .env.example .env     # add your OPENAI_API_KEY + GITHUB_TOKEN
docker compose up --build
```

Test it:
```bash
curl http://localhost:8080/examples/hello.sh
```

## Project Structure

```
scripts/
├── lib/
│   ├── llm.py          # Python LLM wrapper (ask, chat, stream, ask_json, embed)
│   └── llm.js          # Node.js LLM wrapper (same API)
├── examples/
│   ├── hello.sh         # Health check
│   ├── summarize.py     # AI text summarization
│   ├── translate.py     # AI translation
│   ├── sentiment.py     # Sentiment analysis
│   ├── extract.py       # Structured data extraction
│   ├── chat-bot.js      # Chatbot with personas
│   ├── webhook-router.js # Classify incoming webhooks
│   └── generate-sql.js  # Natural language → SQL
└── qodo/
    ├── review.sh         # Qodo code review on a PR
    ├── improve.sh        # Qodo improvement suggestions
    ├── describe.sh       # Auto-generate PR description
    ├── full-suite.sh     # Run all 3 sequentially
    └── github-webhook.py # Auto-router for GitHub PR events
```

## LLM Wrapper

Zero-config — just set `OPENAI_API_KEY` and import:

**Python:**
```python
from lib.llm import ask, ask_json, stream

answer = ask("What is Docker?")
data = ask_json("List 3 colors as JSON")
for chunk in stream("Tell me a story"):
    print(chunk, end="")
```

**Node.js:**
```js
const { ask, askJson, stream } = require('./lib/llm');

const answer = await ask("What is Docker?");
const data = await askJson("List 3 colors");
for await (const chunk of stream("Tell me a story")) {
    process.stdout.write(chunk);
}
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

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key (used by LLM lib + Qodo) |
| `GITHUB_TOKEN` | For Qodo | GitHub PAT with `repo` scope |
| `LLM_BASE_URL` | No | Custom base URL (proxies, local LLMs) |
| `LLM_MODEL` | No | Default model (default: `gpt-4o-mini`) |

## License

MIT
