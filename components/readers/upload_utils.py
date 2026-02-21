"""
Streamlit upload persistence utilities.
"""
from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path
from typing import Tuple


def persist_streamlit_upload(
    uploaded_file,
    *,
    filename: str,
    target_dir: str = "uploads",
    chunk_size: int = 8 * 1024 * 1024,
) -> Tuple[str, str]:
    """Persist a Streamlit UploadedFile to disk without calling ``.getvalue()``.

    Returns:
        ``(path, md5_hex)``
    """
    Path(target_dir).mkdir(parents=True, exist_ok=True)

    suffix = "".join(Path(filename).suffixes) or Path(filename).suffix
    if not suffix:
        suffix = ".bin"

    md5 = hashlib.md5()

    try:
        uploaded_file.seek(0)
    except Exception:
        pass

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=target_dir) as tmp:
        while True:
            chunk = uploaded_file.read(chunk_size)
            if not chunk:
                break
            md5.update(chunk)
            tmp.write(chunk)

        tmp_path = tmp.name

    try:
        uploaded_file.seek(0)
    except Exception:
        pass

    return tmp_path, md5.hexdigest()
