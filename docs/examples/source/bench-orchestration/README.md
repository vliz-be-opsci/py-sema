# sema-bench orchestration example

This folder contains runnable assets for the scenarios described in `examples/bench_orchestration.py`.

## Contents
- `config/sembench.yaml`: two-service workflow that validates `data/persons.ttl` with SHACL and then runs `sema-query` to extract a CSV.
- `config/pipeline.yaml`: three-step workflow that harvests from a local Turtle file, validates the harvested graph, and runs an aggregate query.
- `config/harvest_config.yaml`: harvest configuration used by the pipeline workflow.
- `config/logging.yml`: optional logging setup you can pass with `--logconf`.
- `data/`: input RDF files (`persons.ttl` and harvested output).
- `shapes/`: SHACL shapes for validation.
- `templates/`: SPARQL templates used by `sema-query`.
- `reports/` and `results/`: output folders for SHACL reports and query exports.

## Quick start
From this folder, run the same commands shown in `bench_orchestration.py`:

Use the repo’s virtualenv python (as we tested) to invoke the runner script:

```bash
# Basic validation + extraction
python run_bench.py --config-name sembench.yaml

# Use an alternative config file (the pipeline example)
python run_bench.py --config-name pipeline.yaml

# Continuous monitoring (re-run every 60 seconds)
python run_bench.py --config-name sembench.yaml --interval 60 --watch

# Development mode (fail fast) with logging
python run_bench.py --config-name sembench.yaml --fail-fast --logconf config/logging.yml

# Location mappings (paths become portable across machines)
# (not wired in run_bench.py yet; use the CLI if needed)
# python -m sema.bench --config-path ./config --locations input ./data --locations output ./results
```

Outputs are written to `reports/` and `results/`. After running the pipeline, inspect:
- `results/extracted.csv` for the basic workflow
- `data/harvested.ttl`, `reports/harvest_validation.ttl`, and `results/analysis.csv` for the pipeline workflow

See `sema/bench/README.md` for more background and CLI flags.
