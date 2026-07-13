"""Lightweight LLM wrapper placeholders.

Replace with real integrations (OpenAI, HuggingFace, Ollama, etc.) when available.
"""
from __future__ import annotations

import os
from typing import Optional


def generate_explanation(prompt: str, model: Optional[str] = None) -> str:
    """Return a short explanation string for the given prompt.

    This is a stub — integrate a real LLM in production.
    """
    model = model or os.environ.get("OMNISIGHT_LLM", "local-stub")
    # Very small heuristic stub
    return f"[LLM:{model}] Explanation stub for: {prompt[:200]}"
