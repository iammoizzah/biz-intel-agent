"""
Thin wrapper around the Anthropic client so every agent calls the model
the same way, with the same error handling and token accounting.
"""

import os
from dataclasses import dataclass
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key."
            )
        _client = Anthropic(api_key=api_key)
    return _client


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int


def call_claude(
    system_prompt: str,
    user_message: str,
    model: str,
    max_tokens: int = 2000,
    temperature: float = 0.4,
) -> LLMResponse:
    """Single-turn call. Agents in this system are stateless per-call —
    the orchestrator carries state, not the sub-agents — which keeps
    them simple, parallelizable, and cheap to run on Haiku."""
    client = get_client()
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    text = "".join(block.text for block in resp.content if block.type == "text")
    return LLMResponse(
        text=text,
        input_tokens=resp.usage.input_tokens,
        output_tokens=resp.usage.output_tokens,
    )
