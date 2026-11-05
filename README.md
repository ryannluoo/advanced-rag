# Financial RAG

A compact financial-report RAG engineering project built on the 100 annual reports from Enterprise RAG Challenge Round 2. Evaluation uses unseen questions over this fixed corpus; it does not measure generalization to unseen documents.

## Status

The PDF parsing baseline, page renderer, and token-based chunker are implemented. Parsing produces structured JSON with OCR, layout-aware reading order, native table extraction, and conservative year/value chart recovery. Rendering turns each parsed report into markdown page text. Chunking splits each page into overlapping text chunks with source offsets and citation metadata. Embeddings, indexing, retrieval, and generation remain outside this phase.

## Setup

Use Python 3.12 or later and `uv`. PDF parsing also requires an NVIDIA GPU whose driver supports CUDA 12.6:

```powershell
uv sync --cache-dir .cache/uv --locked --group dev
uv run --cache-dir .cache/uv --locked docling-tools models download -o data/models/docling layout tableformer easyocr --easyocr-lang en
uv run --cache-dir .cache/uv --locked python -m pytest -q
```

Linux and Windows install CUDA 12.6 PyTorch from the PyTorch wheel index. Model artifacts are local and untracked. Runtime and development dependencies are reproducibly locked in `uv.lock`.

## Parsing

Place the source PDFs in `data/raw/reports/`, then run:

```powershell
uv run --cache-dir .cache/uv --locked python -m financial_rag.parsing
```

The parser writes one JSON report per PDF under `data/processed/parsed_reports/`. A directory parse first checks `data/raw/dataset_manifest.json`, then writes `manifest.json` beside the reports only after every JSON report matches that inventory. Explicit input files skip corpus publication:

```powershell
uv run --cache-dir .cache/uv --locked python -m financial_rag.parsing report.pdf --output-dir data/processed/parsed_reports --threads 4
```

See the [PDF parsing specification](specifications/parsing.md) for the fixed composition, output contract, provenance, and failure policy.

## Rendering

```powershell
uv run --cache-dir .cache/uv --locked python -m financial_rag.rendering
```

The renderer reads `data/processed/parsed_reports/` and writes `data/processed/rendered_reports/<document_id>.json`. Each file has `metadata.document_id`, `metadata.page_count`, and `pages`, a list of `{page, text}` in PDF page order. Blocks on a page are separated by a blank line. Table rows and list items stay on single lines. Pages that contain only footers, pictures, or no blocks are omitted. `page_count` still counts every PDF page.

## Chunking

```powershell
uv run --cache-dir .cache/uv --locked python -m financial_rag.chunking
```

The chunker reads `data/processed/rendered_reports/*.json` and writes one `data/processed/chunks/size-<chunk_size>-overlap-<chunk_overlap>/<document_id>.jsonl` per report. Each line contains `metadata` and `text`. Metadata records the chunk ID, document ID, original PDF page, page-local chunk index, token count, and character offsets into the rendered page text.

The baseline uses recursive splitting with the `Qwen/Qwen3-Embedding-0.6B` tokenizer, a chunk size of 384 tokens, and an overlap target of 64 tokens. Each page is split independently; chunks and overlap never cross page boundaries. Only the tokenizer is loaded, so chunking does not require a GPU or embedding-model weights. The tokenizer must be cached locally or downloadable from Hugging Face on first use.

Process selected reports or override the defaults:

```powershell
uv run --cache-dir .cache/uv --locked python -m financial_rag.chunking data/processed/rendered_reports/<document_id>.json
uv run --cache-dir .cache/uv --locked python -m financial_rag.chunking --chunk-size 512 --chunk-overlap 64
```

The second command writes `data/processed/chunks/size-512-overlap-64/`. The default corpus run produced 53,330 chunks across 100 JSONL files in `data/processed/chunks/size-384-overlap-64/`. Generated files remain local and Git-ignored. This stage does not publish a manifest or perform corpus-level validation. See the [chunking specification](specifications/chunking.md) for the schema, splitting behavior, and CLI contract.

## Evaluation

The committed benchmark uses a reproducible 70-question development split and 30-question holdout split. See [evaluation policy](evaluation/README.md).
