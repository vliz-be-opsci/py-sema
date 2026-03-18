# Bench Orchestration Examples

Canonical source README:
<https://github.com/vliz-be-opsci/py-sema/blob/main/examples/bench-orchestration/README.md>

## What this example covers

- Orchestrate multi-step workflows with `sema.bench`.
- Run SHACL validation and query extraction pipelines.
- Switch between basic and pipeline configurations.

## Key assets

- Runner script: `examples/bench-orchestration/run_bench.py`
- Configs: `examples/bench-orchestration/config/*.yaml`
- Data, shapes, templates: `examples/bench-orchestration/data/`, `examples/bench-orchestration/shapes/`, `examples/bench-orchestration/templates/`

## Quick start

```bash
python examples/bench-orchestration/run_bench.py --config-name sembench.yaml
```

## Pipeline workflow

```bash
python examples/bench-orchestration/run_bench.py --config-name pipeline.yaml
```

## Watch mode

```bash
python examples/bench-orchestration/run_bench.py \
	--config-name sembench.yaml \
	--interval 60 \
	--watch
```

## Notes

- Reports are written to `examples/bench-orchestration/reports/`.
- Query outputs are written to `examples/bench-orchestration/results/`.
