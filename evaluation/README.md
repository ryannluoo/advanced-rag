# Evaluation benchmark

This directory defines the reproducible development and holdout split for benchmark v1. The split evaluates generalization to unseen questions over the same fixed document collection; it does not measure generalization to unseen companies or annual reports.

## Files

- `split_config.json` is the authoritative, human-authored split policy.
- `generate_split.py` validates the frozen benchmark and generates the split artifacts.
- `split_manifest.json` records source and output hashes plus realized composition.
- `datasets/development.jsonl` contains the 70 development QA records.
- `datasets/holdout.jsonl` contains the 30 holdout QA records.

The generated files are committed for inspection and reproducibility. Do not edit them manually.

## Split design

The benchmark is split at the question level with seed 42. Stratification preserves question kind, answer category, and reference availability.

| Stratum | Total | Development | Holdout |
| --- | ---: | ---: | ---: |
| `number/value` | 17 | 12 | 5 |
| `number/na` | 41 | 29 | 12 |
| `boolean/true` | 15 | 10 | 5 |
| `boolean/false` | 9 | 6 | 3 |
| `name/value` | 8 | 6 | 2 |
| `name/na` | 1 | 1 | 0 |
| `names/value` | 6 | 4 | 2 |
| `names/na` | 3 | 2 | 1 |
| **Total** | **100** | **70** | **30** |

Reference-backed records are distributed as follows:

| Reference status | Total | Development | Holdout |
| --- | ---: | ---: | ---: |
| With references | 49 | 34 | 15 |
| Without references | 51 | 36 | 15 |

The detailed three-dimensional targets are defined in `split_config.json` and verified by the generator.

## Source integrity and question IDs

The source files under `data/benchmark/` are frozen as benchmark v1. Their expected SHA-256 hashes are stored in `split_config.json`; generation stops if either source changes.

Question IDs are generated from the frozen source positions as `benchmark-v1-q000` through `benchmark-v1-q099`. The source files remain unchanged. A modified or reordered source requires a new benchmark version and regenerated artifacts.

## Usage protocol

Use the development split for repeated system iteration, category analysis, ablations, and failure analysis. Report category results as counts with percentages because the strata are small.

Evaluate the holdout once after the final system configuration is frozen. Report one aggregate score as a fraction with a 95% Wilson interval. Holdout category slices are too small for reliable conclusions.

Gold answers and reference pools are committed in both datasets because they already exist in the public source benchmark. The evaluation layer may read them, but the RAG pipeline must receive only the question ID, question text, and kind.

Experiment outputs belong under `experiments/<run-name>/`, not in this directory. A run should reference question IDs and store its configuration, predictions, and metrics without copying the benchmark records.

## Regeneration

From the repository root, run:

```console
python evaluation/generate_split.py
```

The command validates source hashes and composition before replacing the generated datasets and manifest.
