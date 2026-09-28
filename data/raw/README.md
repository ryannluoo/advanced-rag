# Raw dataset integrity reference

`dataset_manifest.json` is the frozen inventory of the 100 Enterprise RAG
Challenge Round 2 (`ERC2`) PDFs in `reports/`. It is a standalone dataset
prerequisite, independent of parsing, chunking, or other processing.

Treat this file as immutable. Consumers must validate against it, never regenerate
or repair it automatically. An intentional corpus change requires a separately
versioned integrity specification; it must not overwrite this reference.

Each document entry records the lowercase SHA-1 document ID, exact filename,
SHA-1 of the original PDF bytes, and byte size. Entries are sorted by
`document_id`. The raw PDFs are Git-ignored; this reference is not.

## Source

The PDF bytes are not stored in this repository. They are the original
Round 2 annual reports from the
[Enterprise RAG Challenge](https://github.com/trustbit/enterprise-rag-challenge)
repository, under `round2/pdfs/`. Obtain those files separately and place
them in `reports/` using the exact filenames in this reference. This file
inventories that corpus; it does not redistribute it.

## Corpus fingerprint

`corpus_fingerprint` is the lowercase hexadecimal SHA-256 digest computed as follows:

1. Take the manifest fields `dataset_id`, `document_count`, and `documents`,
   excluding `corpus_fingerprint`.
2. Keep document entries sorted by `document_id`.
3. Serialize as compact JSON with object keys sorted recursively, no insignificant
   whitespace, and no trailing newline.
4. Encode as UTF-8 without a BOM, leaving Unicode characters unescaped.
5. Hash those bytes with SHA-256.

The fingerprint is independent of the manifest file's indentation and line
endings. It covers dataset identity, inventory membership, filenames, content
hashes, and byte sizes.

## Document catalog

`document_catalog.json` maps each `document_id` to its `company_name`. It is
the only document metadata available to the pipeline besides the PDFs, and it
is immutable like the manifest. Its keys must equal the manifest's
`document_id` values, and company names must be unique because questions are
routed to reports by company name.

It is derived from `round2/subset.csv` in the ERC2 repository at commit
[`1e348aa`](https://github.com/trustbit/enterprise-rag-challenge/blob/1e348aa6cf43d9d48ae4b0a5b1faf589a8a67591/round2/subset.csv):
`sha1` becomes the key and `company_name` the value. All other columns are
omitted. The yes/no flags are question-generation inputs rather than facts
about the reports: the flag matching each of the 16 development yes/no
questions is true, while 6 of those gold answers are false. `cur` and `major_industry` are wrong for
several well-known companies. A local copy of the source file may be kept as
`subset.csv`; it is Git-ignored.
