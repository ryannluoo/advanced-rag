# Page rendering specification

## Scope

Rendering turns one parsed financial report into markdown page text. It is a deterministic transformation of that JSON. Parsing produces the input. Chunking, embedding, indexing, retrieval, and generation follow this stage.

## Input

The input is one parsed report, as defined in the [PDF parsing specification](parsing.md).

Rendering reads:

- `metadata.document_id`: a non-empty string;
- `metadata.page_count`: an integer greater than or equal to 0;
- `content`: an array of page objects;
- `tables`: an array of table objects.

The report and `metadata` are objects. Each page is an object with an integer `page` of at least 1 and a `content` array of blocks. A missing report `content`, page `content`, or `tables` is an empty array. Any other type for those three members fails rendering.

`page_count` is kept for the output. It is independent of how many pages `content` contains and of how many pages remain after rendering.

Every other member is ignored, including extra metadata, `pictures`, page dimensions, and table fields other than `table_id` and `markdown`.

## Page text

A block is an object. Its `type` is one of `title`, `section_header`, `page_header`, `text`, `caption`, `footnote`, `formula`, `code`, `checkbox_selected`, `checkbox_unselected`, `list_item`, or `table`. Any other type, including a missing type, fails rendering.

`page_footer` and `picture` blocks are dropped. Picture text stays in the ignored `pictures` array.

For every remaining type except `table`, the block text is `text` with leading and trailing whitespace removed. Internal whitespace stays. A missing or null `text` is empty, and a non-string `text` fails rendering. A block whose text is empty is dropped.

What remains is the visible sequence, still in the page's block order. Heading levels and list grouping use this sequence.

### Headings

`title`, `section_header`, and `page_header` become Markdown headings: `# ` or `## `, then the block text.

- A `title` is a first-level heading in any position.
- A `page_header` is a first-level heading in one of the first three visible positions, and a second-level heading after that.
- A `section_header` is a first-level heading only when it is in one of the first three visible positions, none of those three is a `page_header`, and no earlier visible block is a `section_header`. Every other `section_header` is a second-level heading.

An earlier `title` still leaves the next `section_header` eligible for first level. A `page_header` in the first three visible positions makes every `section_header` on that page second level, while each `page_header` in those three positions stays first level.

The visible sequence `section_header`, `section_header` renders a first-level heading and then a second-level heading. The sequence `page_header`, `section_header` does the same.

### Plain text

`text`, `caption`, `footnote`, `formula`, `code`, `checkbox_selected`, and `checkbox_unselected` are the trimmed block text alone.

### Lists

Consecutive `list_item` blocks in the visible sequence form one block. Their lines are separated by a single line break. Dropped blocks do not split a run.

The marker is the block's `marker` when that value is a string, with leading and trailing whitespace removed. Every other marker value is empty.

- A non-empty marker that the text already starts with leaves the line equal to the text.
- When `enumerated` is true and the marker is non-empty, the line is the marker, one space, and the text.
- Otherwise the line is `- ` followed by the text.

### Tables

A `table` block has an integer `table_id`. Rendering inserts the matching table's `markdown` with leading and trailing whitespace removed. Line breaks inside that Markdown stay in place, so each table row remains on one line.

A present `markdown` is a string. A missing `markdown` is empty. Empty Markdown is dropped and is absent from the visible sequence.

A `tables` entry is usable when it is an object with an integer `table_id`. Other entries are ignored. Several entries with the same id resolve to the last one. A `table` block whose id is absent fails rendering.

### Assembly

Each remaining block is one part of the page, and each run of list items is one part. Parts are separated by exactly one blank line. A non-empty page begins at the first part and ends at the last part.

A page with no remaining text is omitted.

Rendered pages follow ascending `page`. Equal page numbers keep their input order. Only pages present in `content` can appear.

## Output document

The rendered object has two members, in order:

1. `metadata`, with `document_id` and `page_count` in that order, both copied from the parsed report;
2. `pages`, an array of `{page, text}` objects, with those members in that order.

An omitted page stays inside `page_count`. A report whose pages are all omitted is still a rendered report, with `pages` equal to an empty array.

## Files

A directory render selects every `*.json` file directly in the input directory, except the file named `manifest.json`, in lexicographic path order. Each selected file is one report. The output file is `<output-directory>/<document_id>.json`.

`document_id` is that filename stem. It must be a single path component: the id and the final component of that id are the same string. `.`, a directory separator, and a trailing separator fail that test, and that report is not written.

When at least one report is selected, rendering creates the output directory if it is absent, then writes reports. No output directory is created when no report is selected. A written report replaces an existing file of the same name. Every other file already in the output directory stays as it is. Rendering writes report files and no publication manifest.

UTF-8, LF newlines, two-space JSON indentation, and preserved Unicode make each file deterministic for a given report.

Positional report paths are the complete input, rendered in the order given. A listed `manifest.json` is included. A missing input directory fails. An input directory with no selected report files fails.

## Failure

Rendering fails when the report, a page, a block, or a table breaks a rule above, when `document_id` is not a valid filename stem, or when an input file is missing, unreadable, or not valid JSON.

The command exits nonzero. Reports already written in that run remain, and a failed run still publishes no manifest.

## Operation

Render every parsed report in the default input directory:

```powershell
uv run --cache-dir .cache/uv --locked python -m financial_rag.rendering
```

The default input directory is `data/processed/parsed_reports`. The default output directory is `data/processed/rendered_reports`.

Render selected reports, or set the output directory:

```powershell
uv run --cache-dir .cache/uv --locked python -m financial_rag.rendering report-a.json report-b.json --output-dir data/processed/rendered_reports
```

Given report paths replace `--input-dir`. On success the command exits 0 and reports how many report files were written and which output directory received them.
