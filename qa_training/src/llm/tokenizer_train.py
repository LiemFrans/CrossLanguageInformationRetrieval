import os
import argparse
from typing import List
from tokenizers import Tokenizer, models, trainers, pre_tokenizers, processors, normalizers

from ..data_loader import load_corpus
from ..hf_loader import load_hf_texts


def train_tokenizer(paths: List[str], out_path: str, vocab_size: int = 16000, hf_dataset: str | None = None, hf_split: str = 'train', hf_text_cols: str | None = None, hf_sample: int | None = None):
    docs = load_corpus(paths)
    if hf_dataset:
        cols = hf_text_cols.split(',') if hf_text_cols else None
        docs += load_hf_texts(hf_dataset, split=hf_split, text_columns=cols, sample=hf_sample)
    if not docs:
        raise SystemExit("No documents found to train tokenizer")
    texts = [t for _, t in docs]

    tok = Tokenizer(models.BPE(unk_token="<unk>"))
    tok.normalizer = normalizers.Sequence([normalizers.NFD(), normalizers.Lowercase()])
    tok.pre_tokenizer = pre_tokenizers.Whitespace()
    tok.post_processor = processors.TemplateProcessing(
        single="<s> $A </s>",
        pair="<s> $A </s> </s> $B </s>",
        special_tokens=[("<s>", 1), ("</s>", 2)],
    )

    trainer = trainers.BpeTrainer(vocab_size=vocab_size, show_progress=True, special_tokens=["<unk>", "<s>", "</s>", "<pad>"])
    tok.train_from_iterator(texts, trainer=trainer)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tok.save(out_path)
    print(f"Saved tokenizer -> {out_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', nargs='+', required=True)
    parser.add_argument('--out', default='qa_training/qa_llm/tokenizer.json')
    parser.add_argument('--hf-dataset', default=None)
    parser.add_argument('--hf-split', default='train')
    parser.add_argument('--hf-text-cols', default=None)
    parser.add_argument('--hf-sample', type=int, default=None)
    parser.add_argument('--vocab-size', type=int, default=16000)
    args = parser.parse_args()

    train_tokenizer(args.inputs, args.out, vocab_size=args.vocab_size, hf_dataset=args.hf_dataset, hf_split=args.hf_split, hf_text_cols=args.hf_text_cols, hf_sample=args.hf_sample)
