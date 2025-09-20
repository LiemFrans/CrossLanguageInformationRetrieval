import os
import argparse
import math
import random
import torch
from torch.utils.data import Dataset, DataLoader
from tokenizers import Tokenizer
from joblib import dump

from ..data_loader import load_corpus
from .model import GPT, GPTConfig
from ..hf_loader import load_hf_texts


class TextDataset(Dataset):
    def __init__(self, text_ids, block_size: int):
        self.data = text_ids
        self.block = block_size
    def __len__(self):
        return max(0, len(self.data) - self.block - 1)
    def __getitem__(self, idx):
        x = self.data[idx:idx+self.block]
        y = self.data[idx+1:idx+self.block+1]
        return torch.tensor(x, dtype=torch.long), torch.tensor(y, dtype=torch.long)


def encode_corpus(tokenizer: Tokenizer, texts, add_special=True):
    ids = []
    for t in texts:
        out = tokenizer.encode(t)
        ids.extend(out.ids)
    return ids


def main():
    parser = argparse.ArgumentParser(description='Train a tiny GPT-like model from scratch')
    parser.add_argument('--inputs', nargs='+', required=True)
    parser.add_argument('--tokenizer', required=True)
    parser.add_argument('--out', default='qa_training/qa_llm')
    parser.add_argument('--n-embd', type=int, default=256)
    parser.add_argument('--n-head', type=int, default=4)
    parser.add_argument('--n-layer', type=int, default=4)
    parser.add_argument('--block-size', type=int, default=256)
    parser.add_argument('--epochs', type=int, default=1)
    parser.add_argument('--batch-size', type=int, default=16)
    parser.add_argument('--lr', type=float, default=3e-4)
    parser.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
    # Optional HF dataset
    parser.add_argument('--hf-dataset', default=None)
    parser.add_argument('--hf-split', default='train')
    parser.add_argument('--hf-text-cols', default=None)
    parser.add_argument('--hf-sample', type=int, default=None)
    args = parser.parse_args()

    # Normalize device argument
    req_dev = str(args.device).lower()
    if req_dev in ('gpu', 'cuda'):
        args.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        args.device = 'cpu'
    if args.device == 'cpu' and req_dev in ('gpu', 'cuda'):
        print("[Info] CUDA not available; falling back to CPU.")

    docs = load_corpus(args.inputs)
    if args.hf_dataset:
        cols = args.hf_text_cols.split(',') if args.hf_text_cols else None
        docs += load_hf_texts(args.hf_dataset, split=args.hf_split, text_columns=cols, sample=args.hf_sample)
    if not docs:
        raise SystemExit('No documents to train on')
    texts = [t for _, t in docs]

    tokenizer = Tokenizer.from_file(args.tokenizer)
    vocab_size = tokenizer.get_vocab_size()

    all_ids = encode_corpus(tokenizer, texts)

    dataset = TextDataset(all_ids, args.block_size)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, drop_last=True)

    cfg = GPTConfig(vocab_size=vocab_size, n_embd=args.n_embd, n_head=args.n_head, n_layer=args.n_layer, block_size=args.block_size)
    model = GPT(cfg).to(args.device)
    optim = torch.optim.AdamW(model.parameters(), lr=args.lr)

    model.train()
    use_amp = (args.device == 'cuda')
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
    for epoch in range(args.epochs):
        total = 0.0
        steps = 0
        for x, y in loader:
            x = x.to(args.device)
            y = y.to(args.device)
            optim.zero_grad(set_to_none=True)
            if use_amp:
                with torch.cuda.amp.autocast():
                    _, loss = model(x, y)
                scaler.scale(loss).backward()
                scaler.step(optim)
                scaler.update()
            else:
                _, loss = model(x, y)
                loss.backward()
                optim.step()
            total += loss.item()
            steps += 1
            if steps % 50 == 0:
                print(f"epoch {epoch} step {steps} loss {total/steps:.4f}")
        print(f"epoch {epoch} avg loss: {total/max(1,steps):.4f}")

    os.makedirs(args.out, exist_ok=True)
    torch.save({'model_state': model.state_dict(), 'config': cfg.__dict__}, os.path.join(args.out, 'llm.pt'))
    print(f"Saved model -> {os.path.join(args.out, 'llm.pt')}")

if __name__ == '__main__':
    main()
