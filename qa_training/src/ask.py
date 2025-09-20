import os
import argparse
from typing import List, Tuple
from joblib import load
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .preprocess import preprocess


def top_k(query: str, model_path: str, k: int = 5) -> List[Tuple[str, float, str]]:
    data = load(model_path)
    vectorizer = data['vectorizer']
    X = data['X']
    names = data['names']
    raw_texts = data['raw_texts']

    q = preprocess(query)
    qv = vectorizer.transform([q])
    sims = cosine_similarity(qv, X)[0]
    idx = np.argsort(-sims)[:k]
    return [(names[i], float(sims[i]), raw_texts[i]) for i in idx]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Query trained TF-IDF model')
    parser.add_argument('--model', default='qa_model/tfidf_model.joblib', help='Path to joblib model file')
    parser.add_argument('--k', type=int, default=5, help='Top-K documents to return')
    args = parser.parse_args()

    print("Type your question (CTRL+C to exit):")
    while True:
        try:
            q = input('> ').strip()
            if not q:
                continue
            results = top_k(q, args.model, k=args.k)
            print("\nTop results:")
            for rank, (name, score, text) in enumerate(results, 1):
                pretty = name.replace('#para=', ' [para ').replace('#sent=', ' [sent ').replace(':', ': ') \
                          .replace(' [para ', ' [para ').replace(' [sent ', ' [sent ') + (']' if '#para=' in name or '#sent=' in name else '')
                print(f"{rank}. {pretty}  (score={score:.4f})")
                snippet = text.strip().replace('\n', ' ')
                if len(snippet) > 300:
                    snippet = snippet[:300] + '...'
                print(f"   {snippet}\n")
        except KeyboardInterrupt:
            print("\nBye")
            break
