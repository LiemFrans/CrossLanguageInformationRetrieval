import os
import io
import chardet
from typing import List, Tuple

try:
    import rarfile  # type: ignore
    RAR_AVAILABLE = True
except Exception:
    RAR_AVAILABLE = False


def read_text_file(path: str) -> str:
    with open(path, 'rb') as f:
        raw = f.read()
    enc = chardet.detect(raw).get('encoding') or 'utf-8'
    try:
        return raw.decode(enc, errors='replace')
    except LookupError:
        return raw.decode('utf-8', errors='replace')


def walk_texts_in_folder(folder: str) -> List[Tuple[str, str]]:
    docs: List[Tuple[str, str]] = []
    for root, _, files in os.walk(folder):
        for fn in files:
            if fn.lower().endswith(('.txt', '.md', '.text')):
                path = os.path.join(root, fn)
                try:
                    content = read_text_file(path)
                    docs.append((path, content))
                except Exception:
                    # skip unreadable files
                    continue
    return docs


def read_rar(rar_path: str) -> List[Tuple[str, str]]:
    if not RAR_AVAILABLE:
        raise RuntimeError("rarfile module not available. Install 'rarfile' and ensure 'unrar' or 'bsdtar' is installed.")
    rf = rarfile.RarFile(rar_path)
    docs: List[Tuple[str, str]] = []
    for info in rf.infolist():
        if info.is_dir():
            continue
        name = info.filename
        if not name.lower().endswith(('.txt', '.md', '.text')):
            continue
        try:
            with rf.open(info, 'r') as f:
                raw = f.read()
            enc = chardet.detect(raw).get('encoding') or 'utf-8'
            try:
                text = raw.decode(enc, errors='replace')
            except LookupError:
                text = raw.decode('utf-8', errors='replace')
            docs.append((f"{rar_path}:{name}", text))
        except Exception:
            # Skip unreadable/corrupted entry
            continue
    return docs


def load_corpus(paths: List[str]) -> List[Tuple[str, str]]:
    all_docs: List[Tuple[str, str]] = []
    for p in paths:
        p = os.path.abspath(p)
        if os.path.isdir(p):
            all_docs.extend(walk_texts_in_folder(p))
        elif os.path.isfile(p) and p.lower().endswith('.rar'):
            all_docs.extend(read_rar(p))
        else:
            # unsupported entry, skip
            continue
    # deduplicate by path key if duplicates
    seen = set()
    unique_docs: List[Tuple[str, str]] = []
    for k, v in all_docs:
        if k in seen:
            continue
        seen.add(k)
        unique_docs.append((k, v))
    return unique_docs
