import os
import argparse
from typing import List, Optional, Tuple
from joblib import dump
from tqdm import tqdm

from .data_loader import load_corpus
from .preprocess import preprocess
from .chunker import split_into_paragraphs, split_into_sentences
from .hf_loader import load_hf_texts

from sklearn.feature_extraction.text import TfidfVectorizer


def train(paths: List[str], out_dir: str, max_features: int = 50000, granularity: str = 'doc', extra_docs: Optional[List[Tuple[str,str]]] = None):
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

    texts = [preprocess(t) for t in tqdm(raw_chunks, desc="Preprocess", unit="chunk")]

    print("Vectorizing with TF-IDF...")
    vectorizer = TfidfVectorizer(
        lowercase=False,
        analyzer='word',
        token_pattern=r"[^\s]+",
        max_features=max_features,
        ngram_range=(1,2)
    )
    X = vectorizer.fit_transform(texts)

    dump({
        'vectorizer': vectorizer,
        'X': X,
        'names': expanded_names,
        'raw_texts': raw_chunks,
        'proc_texts': texts,
        'granularity': granularity,
    }, os.path.join(out_dir, 'tfidf_model.joblib'))
    print(f"Saved model with {X.shape[0]} documents and {X.shape[1]} features -> {os.path.join(out_dir, 'tfidf_model.joblib')}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train TF-IDF retrieval model from RAR archives or folders")
    parser.add_argument('--inputs', nargs='*', default=[], help='Paths to .rar files or folders (optional if using --hf-dataset)')
    parser.add_argument('--out', default='qa_model', help='Output directory to store the model artifacts')
    parser.add_argument('--max-features', type=int, default=50000)
    parser.add_argument('--granularity', choices=['doc','para','sent'], default='doc')
    # Optional HF dataset
    parser.add_argument('--hf-dataset', default=None, help='Add a Hugging Face dataset name, e.g., Deddy/Indonesia-dataset-2023')
    parser.add_argument('--hf-split', default='train')
    parser.add_argument('--hf-text-cols', default=None, help='Comma-separated text column names')
    parser.add_argument('--hf-sample', type=int, default=None, help='Limit number of rows from HF dataset')
    args = parser.parse_args()

    # Load optional HF dataset
    extra_docs = None
    if args.hf_dataset:
        cols = args.hf_text_cols.split(',') if args.hf_text_cols else None
        extra_docs = load_hf_texts(args.hf_dataset, split=args.hf_split, text_columns=cols, sample=args.hf_sample)

    train(args.inputs, args.out, max_features=args.max_features, granularity=args.granularity, extra_docs=extra_docs)
