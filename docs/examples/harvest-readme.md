# Harvest Examples

Canonical source README:
<https://github.com/vliz-be-opsci/py-sema/blob/main/examples/harvest/README.md>

## What this example covers

- Run harvesting jobs with `sema.harvest` from config.
- Dump harvested triples to Turtle output.
- Apply path assertions and optional logging.

## Key assets

- Config: `examples/harvest/config/harvest.yaml`
- Logging config: `examples/harvest/logging.yml`
- Outputs: `examples/harvest/results/`, `examples/harvest/logs/`

## Quick start

```bash
python -m sema.harvest \
	--config examples/harvest/config/harvest.yaml \
	--dump examples/harvest/results/python.ttl
```

## With logging enabled

```bash
python -m sema.harvest \
	--config examples/harvest/config/harvest.yaml \
	--dump examples/harvest/results/python.ttl \
	--logconf examples/harvest/logging.yml
```

## Notes

- The sample harvest config relies on DBpedia and needs network access.
- Keep subject IRIs consistent with harvested triples (for DBpedia, `http://`).
