# sema.query examples

This folder contains hands-on examples for the sema.query module and its CLI tool sema-query. The focus is on practical, copy-ready command lines and clear explanations of what each query does.

For full module documentation, see [sema/query/README.md](../../sema/query/README.md).

## Included files

This example set ships with ready-to-run RDF data, templates, and an output folder:

- Data: [examples/query/data/people.ttl](../query/data/people.ttl), [examples/query/data/organizations.ttl](../query/data/organizations.ttl)
- Templates: [examples/query/templates/people-list.sparql](../query/templates/people-list.sparql), [examples/query/templates/people-by-org.sparql](../query/templates/people-by-org.sparql), [examples/query/templates/org-member-count.sparql](../query/templates/org-member-count.sparql)
- Output: [examples/query/output/.gitkeep](../query/output/.gitkeep)

You can run the commands below from the repository root.

## Quick start (embedded templates)

```bash
# Extract the first 10 triples from a local RDF file
sema-query \
  --source examples/query/data/people.ttl \
  --template_name all.sparql \
  --variables N=10 \
  --output_location examples/query/output/triples.csv
```

What you can do:
- Preview a dataset in seconds before building deeper queries.
- Use the same command against an endpoint by replacing data.ttl with a URL.

## Inspect types in a graph

```bash
sema-query \
  --source examples/query/data/people.ttl \
  --template_name rdf-types.sparql \
  --variables regex=Person \
  --output_location examples/query/output/types.csv
```

What you can do:
- Discover the classes present in an RDF dataset.
- Filter results with regex when the graph is large.

## List BODC collection members (endpoint)

```bash
sema-query \
  --source http://vocab.nerc.ac.uk/sparql/sparql \
  --template_name bodc-listing.sparql \
  --variables cc=P06 lang=en N=50 \
  --output_location examples/query/output/p06-members.csv
```

What you can do:
- Fetch a known collection with a controlled limit.
- Export to CSV for QA or reporting.

## List BODC collection members (local dump)

```bash
sema-query \
  --source ../../tests/query/sources/bodc/20230605-P06-dump.ttl \
  --template_name bodc-listing.sparql \
  --variables cc=P06 lang=en \
  --output_location examples/query/output/p06-dump.csv
```

What you can do:
- Compare local dumps with endpoint output.
- Create reproducible CSVs for downstream workflows.

## Search across multiple collections

```bash
sema-query \
  --source http://vocab.nerc.ac.uk/sparql/sparql \
  --template_name bodc-find.sparql \
  --variables collections[]=P01,P06 regex=.*orca.* language=en \
  --output_location examples/query/output/bodc-find.csv
```

What you can do:
- Find terms by label across collections.
- Use regex for targeted queries.

## Use a custom template folder

```bash
sema-query \
  --source examples/query/data/people.ttl \
  --template_folder examples/query/templates \
  --template_name people-list.sparql \
  --variables limit=25 type=Person \
  --output_location examples/query/output/people.csv
```

What you can do:
- Build a library of reusable queries for your domain.
- Keep templates in version control next to your data.

## Local walkthrough with the included files

### 1) List people and their org membership

```bash
sema-query \
  --source examples/query/data/people.ttl examples/query/data/organizations.ttl \
  --template_folder examples/query/templates \
  --template_name people-by-org.sparql \
  --output_location examples/query/output/people-by-org.csv
```

### 2) Filter by role using a template variable

```bash
sema-query \
  --source examples/query/data/people.ttl \
  --template_folder examples/query/templates \
  --template_name people-list.sparql \
  --variables role=Engineer limit=10 \
  --output_location examples/query/output/people-engineers.csv
```

### 3) Count members per organization

```bash
sema-query \
  --source examples/query/data/people.ttl examples/query/data/organizations.ttl \
  --template_folder examples/query/templates \
  --template_name org-member-count.sparql \
  --output_location examples/query/output/org-member-count.csv
```

## CLI variable formats

The CLI supports three variable styles:

- key=value for single values
- list_key[]=a,b,c for lists
- dict_key.one=1 for single-level dicts

Examples:

```bash
# Single value
sema-query -s examples/query/data/people.ttl -t all.sparql -v N=10 -o examples/query/output/out.csv

# List values
sema-query -s endpoint -t bodc-find.sparql -v collections[]=P01,P06 -o out.csv

# Dict-like values
sema-query -s examples/query/data/people.ttl -t my-template.sparql -v filters.one=foo filters.two=bar -o examples/query/output/out.csv
```

Note: you cannot mix files and endpoints in a single --source list.
