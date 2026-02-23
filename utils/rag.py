from __future__ import annotations

from pathlib import Path
from typing import List, Optional

# Prefer new packages; fall back for compatibility.
try:
    from langchain_ollama import OllamaEmbeddings
except Exception:  # pragma: no cover
    from langchain_community.embeddings import OllamaEmbeddings

try:
    from langchain_chroma import Chroma
except Exception:  # pragma: no cover
    from langchain_community.vectorstores import Chroma

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

_PDF_DIR = Path("memory/pdfs")
_MD_DIR = Path("memory/md")
_CHROMA_DIR = Path("memory/chroma")
_COLLECTION = "cleaning_strategies"
_EMBED_MODEL = "nomic-embed-text"

_vectorstore: Optional[Chroma] = None


def _get_ollama_base_url() -> str | None:
    # Keep consistent with utils/llm.py
    import os

    return os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST") or None


def _get_embed_model() -> str:
    import os

    return os.getenv("OLLAMA_EMBED_MODEL", _EMBED_MODEL)


def _truncate(text: str, max_chars: int) -> str:
    if max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit("\n", 1)[0].strip() + "\n"


def convert_pdfs_to_markdown(pdf_dir: Path = _PDF_DIR, md_dir: Path = _MD_DIR) -> List[Path]:
    """
    Converts each PDF in memory/pdfs into a simple Markdown file in memory/md.
    This is intentionally lightweight: headings by file + per-page sections.
    """
    md_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted([p for p in pdf_dir.glob("*.pdf") if p.is_file()])
    out_paths: List[Path] = []

    # Prefer PyMuPDF for more reliable extraction; fall back to pypdf.
    try:
        import fitz  # pymupdf
        for pdf in pdfs:
            out_md = md_dir / f"{pdf.stem}.md"
            if out_md.exists():
                out_paths.append(out_md)
                continue

            doc = fitz.open(pdf)
            parts = [f"# {pdf.stem}\n"]
            for i, page in enumerate(doc, start=1):
                text = page.get_text("text").strip()
                if not text:
                    continue
                parts.append(f"## Page {i}\n\n{text}\n")
            out_md.write_text("\n".join(parts), encoding="utf-8")
            out_paths.append(out_md)

    except Exception:
        from pypdf import PdfReader
        for pdf in pdfs:
            out_md = md_dir / f"{pdf.stem}.md"
            if out_md.exists():
                out_paths.append(out_md)
                continue

            reader = PdfReader(str(pdf))
            parts = [f"# {pdf.stem}\n"]
            for i, page in enumerate(reader.pages, start=1):
                text = (page.extract_text() or "").strip()
                if not text:
                    continue
                parts.append(f"## Page {i}\n\n{text}\n")
            out_md.write_text("\n".join(parts), encoding="utf-8")
            out_paths.append(out_md)

    return out_paths


def build_or_load_vectorstore(force_reindex: bool = False) -> Optional[Chroma]:
    """
    Builds/loads a persistent Chroma index from Markdown in memory/md.
    Returns None if there is nothing to index.
    """
    _CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure markdown exists (generated from PDFs).
    convert_pdfs_to_markdown()

    md_files = sorted([p for p in _MD_DIR.rglob("*.md") if p.is_file()])
    if not md_files:
        return None

    embed_kwargs: dict = {"model": _get_embed_model()}
    base_url = _get_ollama_base_url()
    if base_url:
        embed_kwargs["base_url"] = base_url

    embeddings = OllamaEmbeddings(**embed_kwargs)

    chroma_sqlite = _CHROMA_DIR / "chroma.sqlite3"
    if chroma_sqlite.exists() and not force_reindex:
        return Chroma(
            persist_directory=str(_CHROMA_DIR),
            embedding_function=embeddings,
            collection_name=_COLLECTION,
        )

    docs = []
    for md in md_files:
        loader = TextLoader(str(md), encoding="utf-8")
        loaded = loader.load()
        for d in loaded:
            d.metadata["source"] = str(md)
        docs.extend(loaded)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    vs = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(_CHROMA_DIR),
        collection_name=_COLLECTION,
    )
    return vs


def _get_vectorstore() -> Optional[Chroma]:
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = build_or_load_vectorstore()
    return _vectorstore


def retrieve_strategy_context(dataset_query: str, k: int = 5, max_chars: int = 3000) -> str:
    """
    Retrieves relevant data cleaning strategies from the knowledge base.
    Query should describe the dataset characteristics and issues.

    Returns an empty string when the vector store is unavailable (e.g. no
    Ollama on Streamlit Cloud) so the pipeline still completes successfully.
    """
    try:
        vs = _get_vectorstore()
    except Exception:
        # Embeddings provider unavailable (e.g. Ollama not running)
        return ""

    if vs is None:
        return ""

    query = (
        "Find relevant data cleaning strategies, best practices, and solutions "
        "for datasets with similar characteristics and issues.\n\n"
        f"DATASET CONTEXT:\n{dataset_query}"
    )

    try:
        # Prefer diverse snippets if available.
        try:
            results = vs.max_marginal_relevance_search(query, k=k, fetch_k=max(12, k * 3))
        except Exception:
            results = vs.similarity_search(query, k=k)
    except Exception:
        # Connection to embedding provider failed during query
        return ""

    lines: List[str] = []
    for d in results:
        src = Path(d.metadata.get("source", "unknown")).name
        snippet = (d.page_content or "").strip()
        if snippet:
            lines.append(f"[{src}] {snippet}")

    return _truncate("\n\n".join(lines), max_chars=max_chars)