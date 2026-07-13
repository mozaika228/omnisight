from __future__ import annotations

from .llm import generate_explanation


def explain_node(module_name: str, context: str) -> str:
    prompt = f"Explain this module `{module_name}` in the repository. Context:\n{context}"
    return generate_explanation(prompt)
