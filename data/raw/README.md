# Raw dataset integrity reference

`dataset_manifest.json` is the frozen inventory of the 100 Enterprise RAG
Challenge Round 2 (`erc2`) PDFs in `documents/`. It is a standalone dataset
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
them in `documents/` using the exact filenames in this reference. This file
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
