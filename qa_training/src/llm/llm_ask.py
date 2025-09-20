import os
import argparse
import torch
from tokenizers import Tokenizer
from .model import GPT, GPTConfig

@torch.no_grad()
def generate_text(model: GPT, tokenizer: Tokenizer, prompt: str, device: str, max_new_tokens: int = 100):
    ids = tokenizer.encode(prompt).ids
    x = torch.tensor([ids], dtype=torch.long, device=device)
    y = model.generate(x, max_new_tokens=max_new_tokens, temperature=0.8, top_k=50)
    out_ids = y[0].tolist()
    return tokenizer.decode(out_ids)


def main():
    parser = argparse.ArgumentParser(description='Generate text from the scratch-trained LLM')
    parser.add_argument('--model', default='qa_training/qa_llm/llm.pt')
    parser.add_argument('--tokenizer', default='qa_training/qa_llm/tokenizer.json')
    parser.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
    args = parser.parse_args()

    req_dev = str(args.device).lower()
    if req_dev in ('gpu','cuda'):
        args.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        args.device = 'cpu'
    if args.device == 'cpu' and req_dev in ('gpu','cuda'):
        print('[Info] CUDA not available; using CPU for generation.')

    ckpt = torch.load(args.model, map_location=args.device)
    cfg = GPTConfig(**ckpt['config'])
    model = GPT(cfg).to(args.device)
    model.load_state_dict(ckpt['model_state'])
    model.eval()

    tokenizer = Tokenizer.from_file(args.tokenizer)

    print("Type your prompt (CTRL+C to exit):")
    while True:
        try:
            p = input('> ').strip()
            if not p:
                continue
            text = generate_text(model, tokenizer, p, args.device, max_new_tokens=100)
            print(f"\n{text}\n")
        except KeyboardInterrupt:
            print("\nBye")
            break

if __name__ == '__main__':
    main()
