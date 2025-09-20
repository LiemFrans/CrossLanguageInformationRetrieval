import os
import argparse
from typing import List, Tuple

import numpy as np
from numpy.linalg import norm
from joblib import load
from sentence_transformers import SentenceTransformer
import torch

from .preprocess import normalize


def cosine_sim(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a @ b.T)


def top_k(query: str, model_path: str, k: int = 5, device: str | None = None) -> List[Tuple[str, float, str]]:
    data = load(model_path)
    # Resolve device
    if device is None:
        resolved = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        dv = str(device).lower()
        if dv in ('gpu','cuda'):
            resolved = 'cuda' if torch.cuda.is_available() else 'cpu'
            if resolved == 'cpu':
                print('[Info] CUDA not available; using CPU for query embeddings.')
        else:
            resolved = 'cpu'
    model = SentenceTransformer(data['model_name'], device=resolved)

    q = normalize(query)
    qv = model.encode([q], normalize_embeddings=True)
    embs = data['embeddings']

    sims = cosine_sim(qv, embs)[0]
    idx = np.argsort(-sims)[:k]
    names = data['names']
    raw_texts = data['raw_texts']
    return [(names[i], float(sims[i]), raw_texts[i]) for i in idx]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Query DL embeddings model')
    parser.add_argument('--model', default='qa_training/qa_model_dl/dl_model.joblib')
    parser.add_argument('--k', type=int, default=5)
    parser.add_argument('--device', default=None, help="'gpu' or 'cpu' (defaults to auto)")
    args = parser.parse_args()

    print("Type your question (CTRL+C to exit):")
    while True:
        try:
            q = input('> ').strip()
            if not q:
                continue
            results = top_k(q, args.model, k=args.k, device=args.device)
            print("\nTop results:")
            for rank, (name, score, text) in enumerate(results, 1):
                print(f"{rank}. {name}  (score={score:.4f})")
                snippet = text.strip().replace('\n', ' ')
                if len(snippet) > 300:
                    snippet = snippet[:300] + '...'
                print(f"   {snippet}\n")
        except KeyboardInterrupt:
            print("\nBye")
            break
