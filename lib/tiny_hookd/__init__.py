"""tiny-hookd LLM library — import from anywhere."""

from tiny_hookd.llm import (
    ask,
    chat,
    ask_json,
    stream,
    embed,
    get_client,
    reset_client,
)

__all__ = ["ask", "chat", "ask_json", "stream", "embed", "get_client", "reset_client"]
