# Subyt Examples

Canonical source README:
<https://github.com/vliz-be-opsci/py-sema/blob/main/examples/subyt/README.md>

## What this example covers

- Generate RDF from CSV and JSON using Jinja2 templates.
- Produce one file per record or one combined output.
- Work with named sets and `no-it` mode.

## Key assets

- Data: `examples/subyt/data/people.csv`, `examples/subyt/data/organizations.csv`, `examples/subyt/data/metadata.json`
- Templates: `examples/subyt/templates/*.ttl`
- Output folder: `examples/subyt/output/`

## Quick start

```bash
sema-subyt \
	--templates examples/subyt/templates \
	--name person.ttl \
	--input examples/subyt/data/people.csv \
	--var base_uri http://example.org/ \
	--output "examples/subyt/output/person-{id}.ttl" \
	--force
```

## Combined catalog (no-it mode)

```bash
sema-subyt \
	--templates examples/subyt/templates \
	--name catalog.ttl \
	--input examples/subyt/data/people.csv \
	--set organizations examples/subyt/data/organizations.csv \
	--set metadata examples/subyt/data/metadata.json \
	--var base_uri http://example.org/ \
	--mode no-it \
	--output examples/subyt/output/catalog.ttl \
	--force
```

## Notes

- Default mode iterates records through `_`.
- `no-it` mode iterates through `sets` and does not expose `_`.
