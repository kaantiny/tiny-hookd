# tiny-hookd 🪝

Battery-included [webhookd](https://github.com/ncarlier/webhookd) Docker setup with Node.js, Python, and LLM libs baked in.

## What's Inside

- **webhookd** — lightweight webhook server (any script = an HTTP endpoint)
- **Node.js 20 LTS** — with OpenAI SDK, Anthropic SDK, retry libs
- **Python 3.11** — with openai, anthropic, tenacity, requests, etc.
- **LLM wrapper libs** — zero-config `ask()` / `chat()` / `stream()` in both Python and JS

## Quick Start

```bash
# 1. Clone
git clone https://github.com/kaantiny/tiny-hookd.git
cd tiny-hookd

# 2. Set up env
cp .env.example .env
# Edit .env with your API keys

# 3. Build & run
docker compose up --build

# 4. Test
curl http://localhost:8080/example.sh
```

## Writing Webhook Scripts

Drop scripts in `./scripts/` — they become HTTP endpoints automatically:

| File | Endpoint |
|------|----------|
| `scripts/example.sh` | `POST /example.sh` |
| `scripts/example.py` | `POST /example.py` |
| `scripts/example.js` | `POST /example.js` |
| `scripts/deploy/notify.sh` | `POST /deploy/notify.sh` |

Scripts receive the HTTP body via **stdin** and return output as the HTTP response.

## LLM Wrapper Libraries

Pre-built wrappers in `scripts/lib/` — just import and call:

### Python

```python
from lib.llm import ask, chat, stream, ask_json, embed

answer = ask("What is Docker?")
answer = ask("Summarize", system="Be concise", model="gpt-4o")
data = ask_json("List 3 colors as JSON")

for chunk in stream("Tell me a story"):
    print(chunk, end="")
```

### Node.js

```js
const { ask, chat, stream, askJson, embed } = require('./lib/llm');

const answer = await ask("What is Docker?");
const data = await askJson("List 3 colors");

for await (const chunk of stream("Tell me a story")) {
    process.stdout.write(chunk);
}
```

### Configuration (via env)

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_API_KEY` / `OPENAI_API_KEY` | — | API key (required) |
| `LLM_BASE_URL` / `OPENAI_BASE_URL` | OpenAI | Base URL (for proxies/local LLMs) |
| `LLM_MODEL` / `OPENAI_MODEL` | `gpt-4o-mini` | Default model |
| `LLM_TEMPERATURE` | `0.7` | Default temperature |
| `LLM_MAX_TOKENS` | `4096` | Default max tokens |

Both wrappers include **automatic retry** with exponential backoff on rate limits (429) and server errors (5xx).

## Docker Compose

```bash
docker compose up --build        # Build & start
docker compose up -d             # Detached
docker compose logs -f webhookd  # Follow logs
docker compose down              # Stop
```

## License

MIT
