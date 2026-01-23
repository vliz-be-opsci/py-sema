"""
sema-syncfs: Filesystem Synchronization Examples

This example demonstrates filesystem to triple store synchronization.
"""

print("=" * 70)
print("sema-syncfs: Filesystem to Triple Store Sync Examples")
print("=" * 70)

# Example 1: Understanding SyncFS
print("\nExample 1: What is sema-syncfs?")
print("-" * 70)
print("""
sema-syncfs synchronizes RDF files with a triple store:
- Automatic loading of RDF files into named graphs
- File watching for real-time updates
- Named graph mapping based on file paths
- Support for multiple RDF formats
""")

# Example 2: File to Graph Mapping
print("\nExample 2: Understanding File-to-Graph Mapping")
print("-" * 70)
print("""
Files are mapped to named graphs based on their path:

Filesystem:
  /root/schemas/person.ttl
  /root/data/persons/alice.ttl
  /root/data/orgs/acme.ttl

With --base http://example.org/sync/:
  → <http://example.org/sync/schemas/person.ttl>
  → <http://example.org/sync/data/persons/alice.ttl>
  → <http://example.org/sync/data/orgs/acme.ttl>

Each file becomes its own named graph in the triple store.
""")

# Example 3: Basic Synchronization
print("\nExample 3: Basic Synchronization")
print("-" * 70)
print("""
# Sync local RDF files to triple store
sema-syncfs \\
  --root /path/to/rdf/files \\
  --store http://localhost:7200/repositories/myrepo \\
          http://localhost:7200/repositories/myrepo/statements

# With custom base URI
sema-syncfs \\
  --root /data/rdf \\
  --base http://example.org/graphs/ \\
  --store http://localhost:7200/repositories/kb \\
          http://localhost:7200/repositories/kb/statements
""")

# Example 4: Development Workflow
print("\nExample 4: Development Workflow")
print("-" * 70)
print("""
# Organize your RDF files
mkdir -p rdf/{schemas,data,metadata}

# Create some RDF files
cat > rdf/schemas/person.ttl << 'EOF'
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex: <http://example.org/> .

ex:Person a rdfs:Class ;
    rdfs:label "Person" .
EOF

cat > rdf/data/alice.ttl << 'EOF'
@prefix ex: <http://example.org/> .

ex:alice a ex:Person ;
    ex:name "Alice" .
EOF

# Sync to development triple store
sema-syncfs \\
  --root rdf/ \\
  --base http://dev.example.org/ \\
  --store http://localhost:7200/repositories/dev \\
          http://localhost:7200/repositories/dev/statements
""")

# Example 5: Production Pipeline
print("\nExample 5: Production Pipeline")
print("-" * 70)
print("""
# Step 1: Generate RDF from data
sema-subyt \\
  --name person_template \\
  --input persons.csv \\
  --output rdf/persons/{id}.ttl

# Step 2: Sync generated files to production
sema-syncfs \\
  --root rdf/ \\
  --base http://example.org/data/ \\
  --store http://triplestore.prod:7200/repositories/knowledge \\
          http://triplestore.prod:7200/repositories/knowledge/statements

# Step 3: Query the synced data
sema-query \\
  --source http://triplestore.prod:7200/repositories/knowledge \\
  --template_name reports.sparql
""")

# Example 6: Querying Named Graphs
print("\nExample 6: Querying Synced Named Graphs")
print("-" * 70)
print("""
After syncing, query specific named graphs:

# Query specific graph
SELECT ?s ?p ?o
FROM <http://example.org/sync/data/alice.ttl>
WHERE {
    ?s ?p ?o .
}

# Query multiple graphs
SELECT ?s ?p ?o
FROM <http://example.org/sync/schemas/person.ttl>
FROM <http://example.org/sync/data/alice.ttl>
WHERE {
    ?s ?p ?o .
}

# Find all synced graphs
SELECT DISTINCT ?g
WHERE {
    GRAPH ?g {
        ?s ?p ?o .
        FILTER(STRSTARTS(STR(?g), "http://example.org/sync/"))
    }
}
""")

# Example 7: Filesystem Organization
print("\nExample 7: Organizing RDF Files")
print("-" * 70)
print("""
Best practice directory structure:

rdf/
├── schemas/           # Ontologies and schemas
│   ├── core.ttl
│   ├── person.ttl
│   └── organization.ttl
├── reference/         # Reference data
│   ├── countries.ttl
│   └── categories.ttl
├── data/              # Instance data
│   ├── persons/
│   │   ├── alice.ttl
│   │   ├── bob.ttl
│   │   └── carol.ttl
│   └── organizations/
│       ├── acme.ttl
│       └── initech.ttl
└── metadata/          # Provenance and metadata
    └── provenance.ttl

Each file syncs to its own named graph, preserving the structure.
""")

# Example 8: Integration Example
print("\nExample 8: Complete Integration Workflow")
print("-" * 70)
print("""
# 1. Harvest external data
sema-harvest \\
  --config harvest_config.yaml \\
  --dump rdf/external/harvested.ttl

# 2. Generate local data from templates
sema-subyt \\
  --name local_data \\
  --input local.csv \\
  --output rdf/local/{id}.ttl

# 3. Sync all to triple store
sema-syncfs \\
  --root rdf/ \\
  --base http://example.org/kb/ \\
  --store http://localhost:7200/repositories/main \\
          http://localhost:7200/repositories/main/statements

# 4. Validate with SHACL
sema-bench \\
  --config-path validation/ \\
  --config-name shacl_validation.yaml

# 5. Query and export results
sema-query \\
  --source http://localhost:7200/repositories/main \\
  --template_name export.sparql \\
  --output_location results.csv
""")

# Example 9: Monitoring and Logging
print("\nExample 9: Monitoring Synchronization")
print("-" * 70)
print("""
# With detailed logging
sema-syncfs \\
  --root rdf/ \\
  --base http://example.org/sync/ \\
  --store http://localhost:7200/repositories/kb \\
          http://localhost:7200/repositories/kb/statements \\
  --logconf logging.yml

# logging.yml example
version: 1
loggers:
  sema.syncfs:
    level: DEBUG
    handlers: [console, file]
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
  file:
    class: logging.FileHandler
    filename: syncfs.log
    level: DEBUG
""")

print("\n" + "=" * 70)
print("Next Steps:")
print("=" * 70)
print("""
1. Organize RDF files in a directory structure
2. Set up a SPARQL endpoint (e.g., GraphDB, Fuseki)
3. Run initial sync: sema-syncfs --root <dir> --store <endpoint>
4. Edit RDF files - changes auto-sync in watch mode
5. Query named graphs using SPARQL FROM clauses
6. See sema/syncfs/README.md for detailed documentation
""")
