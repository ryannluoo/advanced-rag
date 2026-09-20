# PDF parsing specification

## Scope

The baseline converts financial-report PDFs into structured JSON and retrieval-ready text. Parsing ends at this boundary; chunking, indexing, retrieval, and generation are separate stages.

This parser is adapted from the PDF parser in the [Enterprise RAG Challenge Round 2 winning submission](https://github.com/IlyaRice/RAG-Challenge-2) at commit `452d688d1e0d6c3dc5150f9e42c2facb477178b7`. The implementation, API names, module layout, configuration, and command-line interface are localized for this project. The winner report contract is retained so parsing behavior and downstream representation remain consistent.

## Composition

The sole baseline is `financial_rag.parsing.parser.FinancialReportParser`. It uses:

- Docling's maintained `DoclingParseDocumentBackend` and `StandardPdfPipeline`;
- EasyOCR with English recognition and selective OCR;
- TableFormer in accurate mode with PDF-cell matching;
- CUDA acceleration (`device=cuda`) with four CPU threads by default;
- layout and OCR batch size 1, to fit an 8GB GPU;
- CUDA 12.6 PyTorch wheels on Linux and Windows;
- local model artifacts under `data/models/docling`;
- GitHub-flavored Markdown table rendering through `tabulate`.

Parsing requires an NVIDIA GPU and a driver that supports CUDA 12.6. PyTorch does not publish CUDA wheels for macOS; that platform is not a supported parsing host.

Built-in chart extraction is disabled. A deterministic postprocessor promotes a picture only when its text contains consecutive year labels and an equal number of unambiguous currency or percentage values.

The parser rejects retrieval output containing a material concentration of unresolved `/gid` identifiers. A rejected or failed conversion does not produce a successful result.

## Output contract

Each input PDF produces `<stem>.json` and `<stem>.txt` in `data/processed/reports` unless another output directory is selected.

The JSON object has four top-level members, in order:

1. `metainfo`: source stem and document-level item counts;
2. `content`: page-grouped reading-order references to text, tables, and pictures;
3. `tables`: page, bounds, dimensions, Markdown, HTML, and the Docling table object;
4. `pictures`: page, bounds, and recognized child text.

The text file walks `content` in order. Text items are emitted verbatim, table references are replaced with their Markdown tables, and picture references carry no retrieval text unless promoted to tables. UTF-8, LF newlines, two-space JSON indentation, and preserved Unicode make outputs deterministic for a fixed input, dependency lock, and model set.

## Dependencies

Runtime versions are locked in `uv.lock`. Direct parser dependencies are:

- `docling[easyocr]==2.126.0`
- `tabulate==0.10.0`
- `torch==2.14.0` from the PyTorch CUDA 12.6 index on Linux and Windows
- `torchvision==0.29.0` from the same index

PyMuPDF is not a direct or transitive parser dependency.

## Operation

Parsing requires an NVIDIA GPU. Install the environment and local models:

```powershell
uv sync --cache-dir .cache/uv --locked --group dev
uv run --cache-dir .cache/uv --locked docling-tools models download -o data/models/docling layout tableformer easyocr --easyocr-lang en
```

Parse the corpus:

```powershell
uv run --cache-dir .cache/uv --locked python -m financial_rag.parsing
```

Parse selected PDFs or override paths:

```powershell
uv run --cache-dir .cache/uv --locked python -m financial_rag.parsing report-a.pdf report-b.pdf --output-dir data/processed/reports
```

The command exits nonzero when any conversion or output-quality check fails.
