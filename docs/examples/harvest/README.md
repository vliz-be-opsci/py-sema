# sema-harvest example assets

This folder provides a minimal, working harvest configuration you can run directly with the project virtualenv python.

## Contents
- `config/harvest.yaml`: Harvest config that dereferences the DBpedia Python resource, asserts basic paths, and runs a SPARQL subject search on the harvested triples.
- `logging.yml`: Optional logging configuration for `--logconf`.
- Output folders prepared: `results/` and `logs/`.

## Commands (tested)
From `examples/harvest`:

```bash
# Harvest DBpedia Python page and dump triples
python -m sema.harvest \
  --config config/harvest.yaml \
  --dump results/python.ttl

# With logging enabled
python -m sema.harvest \
  --config config/harvest.yaml \
  --dump results/python.ttl \
  --logconf logging.yml
```

Notes:
- The config uses `snooze-till-graph-age-minutes: 1000000` to keep it runnable without admin-graph state.
- Paths asserted on the dereferenced Python resource: `rdf:type` and `rdfs:label`.
- Extra task: SPARQL subject search (`SELECT ?s WHERE { ?s a dbo:ProgrammingLanguage ; rdfs:label "Python (programming language)"@en . }`) with the same `rdf:type` and `rdfs:label` assertions to demonstrate querying harvested triples.
- DBpedia IRIs are `http://` in the retrieved triples; keep the subject URI as `http://dbpedia.org/resource/Python_(programming_language)` (using `https://` will not match and assertions will fail).
- Requires network access to dbpedia.org. If offline, swap the subject URI in `config/harvest.yaml` for a reachable endpoint of your choice.
