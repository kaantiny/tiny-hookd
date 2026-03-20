"""
llm.py - Battery-included LLM wrapper

Usage:
    from lib.llm import ask, chat, stream, embed

    # One-liner
    answer = ask("What is 2+2?")

    # With system prompt
    answer = ask("Summarize this", system="You are a summarizer")

    # Override model per-call
    answer = ask("Hello", model="gpt-4o")

    # Multi-turn conversation
    answer = chat([
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "Hi"},
    ])

    # Streaming
    for chunk in stream("Tell me a story"):
        print(chunk, end="", flush=True)

    # JSON mode
    data = ask_json("List 3 colors as a JSON array")

    # Embeddings
    vec = embed("Hello world")

Env vars:
    OPENAI_API_KEY                    - API key (required)
    LLM_BASE_URL   / OPENAI_BASE_URL  - Base URL (optional, for proxies/local)
    LLM_MODEL                         - Default model (default: gpt-4o-mini)
    LLM_TEMPERATURE                   - Default temperature (default: 0.7)
    LLM_MAX_TOKENS                    - Default max tokens (default: 4096)
"""

import os
import json
from typing import Optional, Generator
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

# --------------- Config from env ---------------

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL") or None
DEFAULT_MODEL = os.getenv("LLM_MODEL") or "gpt-4o-mini"
DEFAULT_TEMP = float(os.getenv("LLM_TEMPERATURE", "0.7"))
DEFAULT_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4096"))

# --------------- Client (singleton) ---------------

_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        kwargs = {}
        if API_KEY:
            kwargs["api_key"] = API_KEY
        if BASE_URL:
            kwargs["base_url"] = BASE_URL
        _client = OpenAI(**kwargs)
    return _client


def reset_client():
    """Force re-create client (e.g. after changing env vars at runtime)."""
    global _client
    _client = None


# --------------- Retry logic ---------------

def _is_retryable(exc):
    """Retry on rate limits (429) and server errors (5xx)."""
    from openai import RateLimitError, APIStatusError
    if isinstance(exc, RateLimitError):
        return True
    if isinstance(exc, APIStatusError) and exc.status_code >= 500:
        return True
    return False


_retry_decorator = retry(
    retry=retry_if_exception(_is_retryable),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True,
)


# --------------- Core functions ---------------

@_retry_decorator
def ask(
    prompt: str,
    *,
    system: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs,
) -> str:
    """Ask a single question, get a string answer."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return chat(messages, model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)


@_retry_decorator
def chat(
    messages: list,
    *,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs,
) -> str:
    """Send a full conversation, get a string answer."""
    resp = get_client().chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
        temperature=temperature if temperature is not None else DEFAULT_TEMP,
        max_tokens=max_tokens or DEFAULT_MAX_TOKENS,
        **kwargs,
    )
    return resp.choices[0].message.content


@_retry_decorator
def ask_json(
    prompt: str,
    *,
    system: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs,
) -> dict | list:
    """Ask and parse the response as JSON. Uses json_object response format."""
    sys_msg = (system or "") + "\nAlways respond with valid JSON."
    messages = [
        {"role": "system", "content": sys_msg.strip()},
        {"role": "user", "content": prompt},
    ]
    resp = get_client().chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=kwargs.pop("temperature", DEFAULT_TEMP),
        max_tokens=kwargs.pop("max_tokens", DEFAULT_MAX_TOKENS),
        **kwargs,
    )
    return json.loads(resp.choices[0].message.content)


def stream(
    prompt: str,
    *,
    system: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs,
) -> Generator[str, None, None]:
    """Stream a response token-by-token."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = get_client().chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
        temperature=temperature if temperature is not None else DEFAULT_TEMP,
        max_tokens=max_tokens or DEFAULT_MAX_TOKENS,
        stream=True,
        **kwargs,
    )
    for chunk in resp:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


@_retry_decorator
def embed(
    text: str | list[str],
    *,
    model: str = "text-embedding-3-small",
) -> list:
    """Get embedding vector(s). Returns single list for string, list of lists for list input."""
    inp = text if isinstance(text, list) else [text]
    resp = get_client().embeddings.create(model=model, input=inp)
    vectors = [d.embedding for d in resp.data]
    return vectors if isinstance(text, list) else vectors[0]
