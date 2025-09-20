# CrossLanguageInformationRetrieval

A combined repository containing:
- A legacy C# Windows Forms project for cross-language information retrieval (CLIR)
- A modern Python "QA Training" pipeline for building searchable models over your documents (RAR/folders), with both TF‑IDF and deep‑learning (sentence embeddings), plus an optional tiny LLM trained from scratch

If your goal is to train and ask questions over your own text collection, use the Python pipeline in `qa_training/`.

## Prerequisites
- `Python 3.11+` (tested on 3.12)
- Linux/macOS/Windows
- Recommended: virtual environment (`venv`)
- Optional for reading `.rar`: `unrar` or `bsdtar`
- Optional GPU: NVIDIA CUDA drivers installed (PyTorch w/ CUDA)

## Setup (Python)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r qa_training/requirements.txt
# Linux: enable RAR reading (optional)
sudo apt-get update && sudo apt-get install -y unrar || sudo apt-get install -y libarchive-tools
```

## Quick Start: Semantic Retrieval (Recommended)
Train multilingual sentence-embedding index on your texts (folder or .rar). Example with a local folder `New folder/Berita`:

```bash
# Train embeddings (granularity: doc | para | sent)
python -m qa_training.src.dl_train \
  --inputs "New folder/Berita" \
  --out qa_training/qa_model_dl \
  --granularity para \
  --device gpu

# Ask questions (interactive)
python -m qa_training.src.dl_ask \
  --model qa_training/qa_model_dl/dl_model.joblib \
  --k 5 \
  --device gpu
```

Tip: You can combine with a public dataset. For example, to include `Deddy/Indonesia-dataset-2023` during training:
```bash
python -m qa_training.src.dl_train \
  --out qa_training/qa_model_dl \
  --hf-dataset Deddy/Indonesia-dataset-2023 \
  --hf-sample 5000 \
  --granularity para \
  --device gpu
```

## Alternative: TF‑IDF Retrieval
```bash
python -m qa_training.src.train \
  --inputs "New folder/Berita" \
  --out qa_training/qa_model \
  --max-features 50000 \
  --granularity sent

python -m qa_training.src.ask --model qa_training/qa_model/tfidf_model.joblib --k 5
```

## Optional: Tiny LLM From Scratch (Experimental)
Train your own tokenizer and a small GPT‑like model. Useful for experiments; for factual QA, prefer retrieval or RAG.

```bash
# 1) Train tokenizer
python -m qa_training.src.llm.tokenizer_train \
  --inputs "New folder/Berita" \
  --out qa_training/qa_llm/tokenizer.json \
  --vocab-size 16000

# 2) Train LLM (1 epoch example)
python -m qa_training.src.llm.llm_train \
  --inputs "New folder/Berita" \
  --tokenizer qa_training/qa_llm/tokenizer.json \
  --out qa_training/qa_llm \
  --epochs 1 --block-size 128 --batch-size 16 \
  --n-embd 192 --n-head 3 --n-layer 3 \
  --device gpu \
  --hf-dataset Deddy/Indonesia-dataset-2023 \
  --hf-sample 5000

# 3) Generate text
python -m qa_training.src.llm.llm_ask \
  --model qa_training/qa_llm/llm.pt \
  --tokenizer qa_training/qa_llm/tokenizer.json \
  --device gpu
```

RAG tip: Use `dl_ask` to retrieve top‑K relevant snippets, then paste them as "Konteks" inside your `llm_ask` prompt for more grounded answers.

## GPU Notes
- All `--device gpu` flags automatically fall back to CPU if CUDA isn’t available.
- Quick CUDA check:
```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

## Repo Structure
- `CrossLanguageInformationRetrieval/` — Original C# WinForms CLIR project
- `qa_training/` — Python retrieval + LLM pipeline (see detailed guide in `qa_training/README.md`)
- `packages/` — NuGet packages for the C# project
- `.gitignore` — ignores build artifacts, model outputs, archives, etc.

## C# Project (Optional)
The original CLIR app is kept for reference. You don’t need to build it to use the Python pipeline. If you do build it, artifacts in `bin/` and `obj/` are ignored by Git.

## Troubleshooting
- RAR reading errors: extract the archive and pass the extracted folder instead of `.rar`.
- Encoding issues: loader auto‑detects encoding with `chardet`.
- LLM quality: small models + few epochs produce limited fluency; use retrieval or RAG for factual answers, and train longer for better generations.

For more examples and advanced usage, read `qa_training/README.md`.
