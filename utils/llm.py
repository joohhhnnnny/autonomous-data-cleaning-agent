import os

from langchain_ollama import OllamaLLM


def _get_ollama_base_url() -> str | None:
	"""Return Ollama base URL if configured.

	Supports both `OLLAMA_BASE_URL` (common in LangChain examples) and
	`OLLAMA_HOST` (commonly used by Ollama tooling). Either should be a full URL
	like `http://localhost:11434`.
	"""
	return os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST") or None


_base_url = _get_ollama_base_url()
_model = os.getenv("OLLAMA_MODEL", "llama3:8b")

try:
	_temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
except ValueError:
	_temperature = 0.7

_kwargs: dict = {"model": _model, "temperature": _temperature}
if _base_url:
	_kwargs["base_url"] = _base_url

llm = OllamaLLM(**_kwargs)