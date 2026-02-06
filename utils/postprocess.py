from __future__ import annotations

import re


_PREAMBLE_PATTERNS = [
    r"^here\s+is\s+my\s+attempt\b.*$",
    r"^here\s+is\s+my\s+take\b.*$",
    r"^here\s+is\s+my\s+rewritten\s+text\b.*$",
    r"^here\s+is\s+my\s+rewrite\b.*$",
    r"^here\s+are\s+\w+\s+versions\b.*$",
    r"^sure[,!]\s+.*$",
    r"^okay[,!]\s+.*$",
]


def strip_model_preamble(text: str) -> str:
    """Remove common LLM meta-prefaces/titles; keep only the rewritten content."""
    if not text:
        return text

    s = text.strip()

    # Remove leading markdown title if the model invents one.
    s = re.sub(r"^#{1,3}\s+.+\n+", "", s, flags=re.IGNORECASE)

    # Remove one or more preamble lines.
    lines = s.splitlines()
    cleaned: list[str] = []
    skipping = True
    for line in lines:
        raw = line.strip()
        if skipping:
            if raw == "":
                continue
            lowered = raw.lower()
            if any(re.match(p, lowered) for p in _PREAMBLE_PATTERNS):
                continue
            # Some models add a colon line like "Rewritten:" then blank.
            if lowered in {"rewritten:", "rewrite:", "output:", "humanized text:"}:
                continue
            skipping = False

        cleaned.append(line)

    return "\n".join(cleaned).strip()
