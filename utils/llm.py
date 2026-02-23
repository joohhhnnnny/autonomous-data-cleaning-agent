"""
LLM provider abstraction.

Supports two back-ends:
  * **Groq** (cloud)  – used when ``GROQ_API_KEY`` is available.
    Set it via environment variable *or* Streamlit secrets.
  * **Ollama** (local) – used as fallback when no Groq key is found.

The exported ``llm`` object always exposes ``.invoke(prompt: str) -> str``.
"""
from __future__ import annotations

import os


# ---------------------------------------------------------------------------
# Helper: resolve a secret from env vars *or* Streamlit secrets
# ---------------------------------------------------------------------------

def _get_secret(name: str) -> str | None:
    """Return a secret value from env vars or ``st.secrets``."""
    val = os.getenv(name)
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get(name)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Ollama helpers (kept for local dev)
# ---------------------------------------------------------------------------

def _get_ollama_base_url() -> str | None:
    return os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST") or None


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

def _build_llm():
    groq_key = _get_secret("GROQ_API_KEY")

    if groq_key:
        # ---- Groq (cloud) ------------------------------------------------
        from langchain_groq import ChatGroq

        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        try:
            temperature = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
        except ValueError:
            temperature = 0.7

        _chat = ChatGroq(api_key=groq_key, model=model, temperature=temperature)

        # Wrap so .invoke() returns a plain string (same as OllamaLLM).
        class _StrLLM:
            """Thin wrapper that returns ``str`` from ``ChatGroq``."""
            def invoke(self, prompt: str) -> str:
                return _chat.invoke(prompt).content

        return _StrLLM()

    # ---- Ollama (local fallback) ------------------------------------------
    from langchain_ollama import OllamaLLM

    base_url = _get_ollama_base_url()
    model = os.getenv("OLLAMA_MODEL", "llama3:8b")
    try:
        temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    except ValueError:
        temperature = 0.7

    kwargs: dict = {"model": model, "temperature": temperature}
    if base_url:
        kwargs["base_url"] = base_url

    return OllamaLLM(**kwargs)


llm = _build_llm()