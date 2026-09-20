# Financial RAG

A compact financial-report RAG engineering project built on the 100 annual reports from Enterprise RAG Challenge Round 2. Evaluation uses unseen questions over this fixed corpus; it does not measure generalization to unseen documents.

## Status

The PDF parsing baseline is implemented. It produces structured JSON and retrieval text with OCR, layout-aware reading order, native table extraction, and conservative year/value chart recovery. Chunking, embeddings, indexing, retrieval, and generation remain outside this phase.

## Setup

Use Python 3.12 or later, `uv`, and an NVIDIA GPU whose driver supports CUDA 12.6:

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

The parser writes one JSON report and one TXT retrieval document per PDF under `data/processed/reports/`. Explicit input files and path overrides are supported:

```powershell
uv run --cache-dir .cache/uv --locked python -m financial_rag.parsing report.pdf --output-dir data/processed/reports --threads 4
```

See the [PDF parsing specification](specifications/parsing.md) for the fixed composition, output contract, provenance, and failure policy.

## Evaluation

The committed benchmark uses a reproducible 70-question development split and 30-question holdout split. See [evaluation policy](evaluation/README.md).
