import re
from typing import List


def split_into_paragraphs(text: str) -> List[str]:
    # Split on two or more newlines, keep non-empty
    parts = re.split(r"\n\s*\n+", text)
    return [p.strip() for p in parts if p and p.strip()]


def split_into_sentences(text: str) -> List[str]:
    # Simple rule-based splitter for ID/EN punctuation
    # Note: for production, consider stanza/spacy; we avoid extra deps here
    # Handle periods, question marks, exclamation, with whitespace following
    # Avoid splitting on common abbreviations (very minimal list)
    abbreviations = set(['dr', 'mr', 'mrs', 'ms', 'no', 'sdr', 'sri', 'pt', 'cv', 'tbk', 'dsb'])
    tokens = re.split(r"(\S+)", text)
    out = []
    buf = []
    for tok in tokens:
        if tok is None:
            continue
        buf.append(tok)
        stripped = tok.strip()
        if not stripped:
            continue
        if stripped[-1:] in ['.', '!', '?']:
            word = stripped[:-1].lower()
            if word not in abbreviations:
                sent = ''.join(buf).strip()
                if sent:
                    out.append(sent)
                buf = []
    # Remainder
    rem = ''.join(buf).strip()
    if rem:
        out.append(rem)
    # Post filter very short sentences
    out = [s for s in out if len(s) >= 2]
    return out
