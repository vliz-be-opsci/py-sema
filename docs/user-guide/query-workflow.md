# Workflow: Query RDF Data

This workflow shows the fastest way to query RDF data with sema-query using the runnable assets in [examples/query](../../examples/query/README.md).

## Goal

Generate CSV outputs from local Turtle files and from a remote SPARQL endpoint.

## Prerequisites

- py-sema installed (see [Getting Started](../getting-started.md))
- Run commands from repository root

## Step 1: Query Local RDF Files

Run a template against bundled local input files:

```bash
sema-query \
  --source examples/query/data/people.ttl examples/query/data/organizations.ttl \
  --template_folder examples/query/templates \
  --template_name people-by-org.sparql \
  --output_location examples/query/output/people-by-org.csv
```

Expected output:

- examples/query/output/people-by-org.csv

## Step 2: Filter Results With Variables

Use template variables to narrow output:

```bash
sema-query \
  --source examples/query/data/people.ttl \
  --template_folder examples/query/templates \
  --template_name people-list.sparql \
  --variables role=Engineer limit=10 \
  --output_location examples/query/output/people-engineers.csv
```

Expected output:

- examples/query/output/people-engineers.csv

## Step 3: Query a Remote Endpoint

Run a built-in template against BODC:

```bash
sema-query \
  --source http://vocab.nerc.ac.uk/sparql/sparql \
  --template_name bodc-listing.sparql \
  --variables cc=P06 lang=en N=50 \
  --output_location examples/query/output/p06-members.csv
```

Expected output:

- examples/query/output/p06-members.csv

## Troubleshooting

If a command fails:

1. Check command options with sema-query --help
2. Confirm paths under examples/query/data and examples/query/templates
3. If querying remote endpoints, verify network access
4. Ensure output directory exists (examples/query/output)

## Canonical Source

For the complete command set and variable formats, see:

- [Query Example README (Included)](../examples/query-readme.md)
