# Query Examples

Canonical source README:
<https://github.com/vliz-be-opsci/py-sema/blob/main/examples/query/README.md>

## What this example covers

- Query local RDF files and SPARQL endpoints with `sema-query`.
- Use built-in query templates and custom template folders.
- Pass CLI template variables for filtering and limits.

## Key assets

- Data: `examples/query/data/people.ttl`, `examples/query/data/organizations.ttl`
- Templates: `examples/query/templates/*.sparql`
- Output folder: `examples/query/output/`

## Quick start

```bash
sema-query \
	--source examples/query/data/people.ttl \
	--template_name all.sparql \
	--variables N=10 \
	--output_location examples/query/output/triples.csv
```

## Local walkthrough

```bash
# 1) People by organization
sema-query \
	--source examples/query/data/people.ttl examples/query/data/organizations.ttl \
	--template_folder examples/query/templates \
	--template_name people-by-org.sparql \
	--output_location examples/query/output/people-by-org.csv

# 2) Filter by role
sema-query \
	--source examples/query/data/people.ttl \
	--template_folder examples/query/templates \
	--template_name people-list.sparql \
	--variables role=Engineer limit=10 \
	--output_location examples/query/output/people-engineers.csv
```

## Notes

- Do not mix local files and endpoints in one `--source` invocation.
- For full command variants and variable formats, use the canonical source README.
