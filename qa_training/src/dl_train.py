import os
import argparse
from typing import List, Optional, Tuple
import torch

import numpy as np
from joblib import dump
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

from .data_loader import load_corpus
from .preprocess import normalize
from .chunker import split_into_paragraphs, split_into_sentences
from .hf_loader import load_hf_texts


def batch_encode(model: SentenceTransformer, texts: List[str], batch_size: int = 32) -> np.ndarray:
    embs = model.encode(texts, batch_size=batch_size, show_progress_bar=True, normalize_embeddings=True)
    return np.asarray(embs, dtype=np.float32)


def dl_train(paths: List[str], out_dir: str, model_name: str = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', batch_size: int = 32, granularity: str = 'doc', device: str | None = None, extra_docs: Optional[List[Tuple[str,str]]] = None):
    os.makedirs(out_dir, exist_ok=True)

    print("Loading documents...")
    docs = load_corpus(paths)
    if extra_docs:
        docs = docs + extra_docs
    if not docs:
        raise SystemExit("No documents found. Provide paths to .rar files or folders containing .txt or specify --hf-dataset")

    # Expand docs by granularity
    expanded_names: List[str] = []
    raw_chunks: List[str] = []
    for p, raw in docs:
        if granularity == 'doc':
            expanded_names.append(p)
            raw_chunks.append(raw)
        elif granularity == 'para':
            for i, chunk in enumerate(split_into_paragraphs(raw)):
                expanded_names.append(f"{p}#para={i}")
                raw_chunks.append(chunk)
        elif granularity == 'sent':
            for i, chunk in enumerate(split_into_sentences(raw)):
                expanded_names.append(f"{p}#sent={i}")
                raw_chunks.append(chunk)
        else:
            raise ValueError("granularity must be one of: 'doc', 'para', 'sent'")

    texts = [normalize(t) for t in raw_chunks]

    # Normalize device alias
    resolved_device: str | None
    if device is None:
        resolved_device = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        dev = str(device).lower()
        if dev in ('gpu', 'cuda'):
            resolved_device = 'cuda' if torch.cuda.is_available() else 'cpu'
            if resolved_device == 'cpu':
                print('[Info] CUDA not available; falling back to CPU for embeddings.')
        else:
            resolved_device = 'cpu'
    print(f"Loading embedding model: {model_name} on device={resolved_device}")
    model = SentenceTransformer(model_name, device=resolved_device)

    print("Encoding documents...")
    embeddings = batch_encode(model, texts, batch_size=batch_size)

    dump({
        'model_name': model_name,
        'names': expanded_names,
        'raw_texts': raw_chunks,
        'norm_texts': texts,
        'granularity': granularity,
        'embeddings': embeddings,
    }, os.path.join(out_dir, 'dl_model.joblib'))
    print(f"Saved embeddings for {embeddings.shape[0]} docs -> {os.path.join(out_dir, 'dl_model.joblib')}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train DL retrieval model (embeddings) from RAR archives or folders')
    parser.add_argument('--inputs', nargs='*', default=[])
    parser.add_argument('--out', default='qa_model_dl')
    parser.add_argument('--model-name', default='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--granularity', choices=['doc','para','sent'], default='doc')
    parser.add_argument('--device', default=None, help="'gpu' or 'cpu' (defaults to auto)")
    # Optional HF dataset
    parser.add_argument('--hf-dataset', default=None, help='Add a Hugging Face dataset name')
    parser.add_argument('--hf-split', default='train')
    parser.add_argument('--hf-text-cols', default=None)
    parser.add_argument('--hf-sample', type=int, default=None)
    args = parser.parse_args()

    extra_docs = None
    if args.hf_dataset:
        cols = args.hf_text_cols.split(',') if args.hf_text_cols else None
        extra_docs = load_hf_texts(args.hf_dataset, split=args.hf_split, text_columns=cols, sample=args.hf_sample)

    dl_train(args.inputs, args.out, model_name=args.model_name, batch_size=args.batch_size, granularity=args.granularity, device=args.device, extra_docs=extra_docs)
