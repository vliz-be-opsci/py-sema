# sema.subyt examples

This folder contains hands-on examples for the sema.subyt module and its CLI tool sema-subyt. It includes small input datasets, Jinja2 RDF templates, and an output folder so you can run the commands as-is.

For full module documentation, see [sema/subyt/README.md](../../sema/subyt/README.md).

## Included files

- Data: [examples/subyt/data/people.csv](../subyt/data/people.csv), [examples/subyt/data/organizations.csv](../subyt/data/organizations.csv), [examples/subyt/data/metadata.json](../subyt/data/metadata.json)
- Templates: [examples/subyt/templates/person.ttl](../subyt/templates/person.ttl), [examples/subyt/templates/catalog.ttl](../subyt/templates/catalog.ttl), [examples/subyt/templates/organizations.ttl](../subyt/templates/organizations.ttl)
- Output: [examples/subyt/output/.gitkeep](../subyt/output/.gitkeep)

You can run the commands below from the repository root.

## 1) Generate one file per person

```bash
sema-subyt \
  --templates examples/subyt/templates \
  --name person.ttl \
  --input examples/subyt/data/people.csv \
  --var base_uri http://example.org/ \
  --output "examples/subyt/output/person-{id}.ttl" \
  --force
```

What you can do:
- Convert a CSV into per-record RDF files.
- Use a URI template in the output path.

## 2) Generate a combined catalog (no-it mode)

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

What you can do:
- Build a single RDF file from multiple datasets.
- Use JSON metadata alongside CSV input.

## 3) Export organizations only

```bash
sema-subyt \
  --templates examples/subyt/templates \
  --name organizations.ttl \
  --set organizations examples/subyt/data/organizations.csv \
  --mode no-it \
  --output examples/subyt/output/organizations.ttl \
  --force
```

What you can do:
- Generate RDF from a named set without a base input.
- Keep templates in version control with their input files.

## 4) Unique filtering

```bash
sema-subyt \
  --templates examples/subyt/templates \
  --name person.ttl \
  --input examples/subyt/data/people.csv \
  --var base_uri http://example.org/ \
  --unique "{id}" \
  --output examples/subyt/output/unique-people.ttl \
  --force
```

What you can do:
- Skip duplicate records based on a URI template pattern.

## Template notes

- When running in default iteration mode, each record is available as `_`.
- In `no-it` mode, no `_` record exists; iterate over `sets` instead.

Example (iteration mode):

```turtle
<{{ base_uri }}person/{{ _.id }}>
    a foaf:Person ;
    foaf:name "{{ _.name }}" .
```

Example (no-it mode):

```turtle
{% for org in sets.organizations %}
<{{ base_uri }}org/{{ org.id }}>
    a schema:Organization ;
    schema:name "{{ org.name }}" .
{% endfor %}
```
