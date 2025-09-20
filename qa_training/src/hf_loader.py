from __future__ import annotations
from typing import List, Tuple, Optional

def load_hf_texts(dataset_name: str, split: str = 'train', text_columns: Optional[List[str]] = None, sample: Optional[int] = None) -> List[Tuple[str, str]]:
    """
    Load texts from a Hugging Face dataset.
    Returns a list of (id, text). If multiple text columns, they are joined with double newlines.
    """
    try:
        from datasets import load_dataset  # type: ignore
    except Exception as e:
        raise RuntimeError("Please install 'datasets' package to use --hf-dataset") from e

    ds = load_dataset(dataset_name, split=split)

    # Auto-detect text columns if none provided
    if text_columns is None:
        # try common column names first
        candidates = ['text', 'content', 'article', 'body', 'paragraph', 'sentence', 'title']
        available = [c for c in candidates if c in ds.column_names]
        if not available:
            # fallback: all string-typed columns
            available = []
            for c in ds.column_names:
                # try to detect string columns by sampling
                val = ds[0][c]
                if isinstance(val, str):
                    available.append(c)
        text_columns = available or [ds.column_names[0]]

    rows = []
    n = len(ds)
    limit = min(sample, n) if isinstance(sample, int) and sample > 0 else n
    for i in range(limit):
        row = ds[i]
        parts: List[str] = []
        for col in text_columns:
            v = row.get(col)
            if isinstance(v, str) and v.strip():
                parts.append(v.strip())
        if not parts:
            continue
        text = "\n\n".join(parts)
        rows.append((f"hf:{dataset_name}:{split}:{i}", text))
    return rows
