from __future__ import annotations
import re
from typing import Iterable, List

# Simple tokenizer and normalizer suitable for Indonesian + English
# Default to safe ASCII pattern; upgrade to Unicode categories if 'regex' is installed.
WORD_RE = re.compile(r"[A-Za-z0-9_]+")

try:
    # 'regex' module supports \p{L}, \p{N} Unicode categories
    import regex as _better_re  # type: ignore
    WORD_RE = _better_re.compile(r"[\p{L}\p{N}_]+", _better_re.UNICODE)
except Exception:
    pass

# Minimal stopwords (Indonesian + English). You can extend via a file later.
ID_STOP = {
    'yang','dan','di','ke','dari','untuk','pada','dengan','atau','juga','itu','ini','adalah','karena','agar','sebagai','dalam','tersebut','bagi','mereka','kami','kita','saya','anda','dia','ia','tidak','ya','bukan','sebuah','para','akan','telah','sudah','belum','lebih','kurang','banyak','sedikit','tanpa','antara','hingga','sampai','oleh','tentang','atas','bawah','setelah','sebelum','kembali'
}
EN_STOP = {
    'the','a','an','and','or','but','if','then','else','for','to','of','in','on','at','by','with','from','as','is','are','was','were','be','been','being','have','has','had','do','does','did','not','no','yes','this','that','these','those','it','its','he','she','they','we','you','i','my','your','their','our','his','her','them','us','me'
}
STOPWORDS = ID_STOP | EN_STOP


def normalize(text: str) -> str:
    text = text.lower()
    # normalize quotes and whitespace
    text = text.replace('\u201c', '"').replace('\u201d', '"').replace('\u2019', "'")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> List[str]:
    text = normalize(text)
    return [t for t in WORD_RE.findall(text)]


def remove_stopwords(tokens: Iterable[str]) -> List[str]:
    return [t for t in tokens if t not in STOPWORDS]


def preprocess(text: str) -> str:
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    return " ".join(tokens)
