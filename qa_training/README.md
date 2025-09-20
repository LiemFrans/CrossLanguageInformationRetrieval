# QA Training (TF-IDF Retrieval)

This mini app trains a TF-IDF retrieval model from your document collections (e.g., `film.rar`, `gadget.rar`, `olahraga.rar`) and lets you ask questions to get the most relevant documents.

## Features
- Reads `.rar` archives directly (requires `unrar` or `bsdtar` installed) and/or folders of `.txt` files
- Simple Indonesian + English preprocessing (lowercasing, tokenization, stopword removal)
- Trains a TF-IDF vector space model with uni/bi-grams
- CLI to query top-K relevant documents
- Deep Learning mode: multilingual sentence embeddings (Sentence-Transformers) for semantic retrieval
 - NLP flow with chunking granularity: per-document, per-paragraph, or per-sentence indexing
 - Optional: Tiny LLM from-scratch (for experimentation): train your own tokenizer + small GPT-like model

## Setup

1) Create and activate a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies

```bash
pip install -r qa_training/requirements.txt
```

Note: For reading `.rar` files, also install a backend on Linux:

```bash
sudo apt-get update
sudo apt-get install -y unrar
```

If `unrar` is not available, install `bsdtar` (`libarchive-tools`) instead.

## Train (TF-IDF)

From the repository root, run:

```bash
# granularity: doc | para | sent (default: doc)
python -m qa_training.src.train --inputs film.rar gadget.rar olahraga.rar --out qa_training/qa_model \
	--max-features 50000
# Tambahkan dataset Hugging Face (opsional):
python -m qa_training.src.train --out qa_training/qa_model --hf-dataset Deddy/Indonesia-dataset-2023 --hf-split train --hf-sample 5000 --granularity sent

# contoh: indexing per-paragraf
python -m qa_training.src.train --inputs "New folder/Berita" --out qa_training/qa_model --max-features 50000 \
  
```

- You can also pass extracted folders instead of `.rar` files.
- The output `tfidf_model.joblib` will be written to `qa_training/qa_model/`.

## Ask Questions (TF-IDF)

```bash
python -m qa_training.src.ask --model qa_training/qa_model/tfidf_model.joblib --k 5
```

Then type your question. The CLI prints the top documents with similarity scores and a short snippet.

## Train (Deep Learning Embeddings)

Multilingual model (Indo/EN) using Sentence-Transformers:

```bash
# granularity: doc | para | sent (default: doc) | device: gpu|cpu (auto)
python -m qa_training.src.dl_train --inputs film.rar gadget.rar olahraga.rar --out qa_training/qa_model_dl \
	--model-name sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 --granularity doc --device gpu
# Tambahkan dataset Hugging Face (opsional):
python -m qa_training.src.dl_train --out qa_training/qa_model_dl --hf-dataset Deddy/Indonesia-dataset-2023 --hf-sample 5000 --granularity para --device gpu

# contoh: indexing per-kalimat (GPU bila tersedia)
python -m qa_training.src.dl_train --inputs "New folder/Berita" --out qa_training/qa_model_dl --granularity sent --device gpu
```

Use folders if RARs have issues:

```bash
python -m qa_training.src.dl_train --inputs "New folder/Berita" --out qa_training/qa_model_dl
```

## Ask Questions (Deep Learning)

```bash
python -m qa_training.src.dl_ask --model qa_training/qa_model_dl/dl_model.joblib --k 5 --device gpu
```

## Notes
- Encoding is auto-detected with `chardet`.
- You can extend stopwords in `qa_training/src/preprocess.py`.
- This is a document retriever. For generative answers, integrate a reader or LLM on top of the retrieved texts.

## (Advanced) Train a Tiny LLM From Scratch

Catatan: Ini untuk eksperimen dan dataset kecil; hasil tidak akan menyaingi LLM besar.

1) Train tokenizer dari korpus Anda:

```bash
python -m qa_training.src.llm.tokenizer_train --inputs "New folder/Berita" --out qa_training/qa_llm/tokenizer.json --vocab-size 16000

# atau gabungkan dataset Hugging Face:
python -m qa_training.src.llm.tokenizer_train --inputs "New folder/Berita" --out qa_training/qa_llm/tokenizer.json \
	--vocab-size 16000 --hf-dataset Deddy/Indonesia-dataset-2023 --hf-sample 5000
```

2) Train model kecil (GPT-like) dari nol (bisa GPU bila tersedia):

```bash
python -m qa_training.src.llm.llm_train --inputs "New folder/Berita" --tokenizer qa_training/qa_llm/tokenizer.json \
	--out qa_training/qa_llm --epochs 1 --block-size 256 --batch-size 16 --n-embd 256 --n-head 4 --n-layer 4 --device gpu

# atau sertakan dataset Hugging Face juga:
python -m qa_training.src.llm.llm_train --inputs "New folder/Berita" --tokenizer qa_training/qa_llm/tokenizer.json \
	--out qa_training/qa_llm --epochs 1 --block-size 256 --batch-size 16 --n-embd 256 --n-head 4 --n-layer 4 --device gpu \
	--hf-dataset Deddy/Indonesia-dataset-2023 --hf-sample 5000
```

3) Generate teks dari model:

```bash
python -m qa_training.src.llm.llm_ask --model qa_training/qa_llm/llm.pt --tokenizer qa_training/qa_llm/tokenizer.json --device gpu
```

### Setelah Menjalankan llm_train: Cara Test Tanya-Jawab

Ada dua cara praktis untuk mengetes hasil Anda:

1) Tanya‑jawab berbasis retriever (disarankan, akurat karena berbasis dokumen):

```bash
python -m qa_training.src.dl_ask \
	--model qa_training/qa_model_dl/dl_model.joblib \
	--k 5 \
	--device gpu
```

Lalu ketik pertanyaan, misalnya:

```
> Apa kebijakan Google terkait sertifikasi perangkat Android baru?
```

Contoh dokumen sumber (ringkas): "Google memberhentikan sertifikasi perangkat baru … sehingga perangkat baru wajib dirilis dengan Android 8.0 Oreo."

2) Generasi jawaban dengan LLM yang baru dilatih (eksperimental, tidak selalu faktual):

```bash
python -m qa_training.src.llm.llm_ask \
	--model qa_training/qa_llm/llm.pt \
	--tokenizer qa_training/qa_llm/tokenizer.json \
	--device gpu
```

Ketik prompt seperti:

```
> Gunakan konteks berikut untuk menjawab singkat. 
> Konteks: Google memberhentikan sertifikasi perangkat Android Nougat, sehingga perangkat Android baru bersertifikasi Google Play wajib dirilis dengan Android 8.0 Oreo. Apa dampaknya bagi vendor?
```

Tips RAG manual: Ambil 2–3 snippet teratas dari `dl_ask` lalu tempel sebagai "Konteks" di prompt `llm_ask` agar jawaban lebih grounded.

### GPU Troubleshooting
- Cek ketersediaan CUDA di Python:
```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```
- Pastikan driver NVIDIA dan versi CUDA yang sesuai terpasang.
- Jika `--device gpu` dipilih tapi CUDA tidak tersedia, script otomatis fallback ke CPU.
