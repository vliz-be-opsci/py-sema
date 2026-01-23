"""
Simple SPARQL Query Example

This example demonstrates how to use py-sema's query CLI tool.
Note: The query module is primarily designed to be used via CLI.
For programmatic usage, refer to the actual source code in sema/query/
"""

print("=" * 60)
print("py-sema Query Examples")
print("=" * 60)

# Example 1: Understanding py-sema query
print("\nExample 1: What does sema-query do?")
print("-" * 60)
print("""
sema-query is a command-line tool for extracting tabular data from 
RDF knowledge graphs using SPARQL templates.

Key features:
- Query RDF files (Turtle, RDF/XML, N-Triples)
- Query SPARQL endpoints
- Use Jinja2 templates for dynamic queries
- Export results to CSV or TSV format
""")

# Example 2: Basic CLI usage
print("\nExample 2: Basic CLI Usage")
print("-" * 60)
print("""
# Query an RDF file and output as CSV
sema-query --source data.ttl --output_format csv

# Query a SPARQL endpoint
sema-query --source http://localhost:7200/repositories/my-repo \\
           --output_format csv

# Get help on all options
sema-query --help
""")

# Example 3: Using templates
print("\nExample 3: Using SPARQL Templates")
print("-" * 60)
print("""
sema-query supports Jinja2 templates for reusable queries:

# Use a template from a folder
sema-query --source data.ttl \\
           --template_folder /path/to/templates \\
           --template_name my_query.sparql \\
           --variables var1=value1 var2=value2 \\
           --output_format csv

Templates allow you to parameterize SPARQL queries and reuse them
across different datasets.
""")

# Example 4: Sample SPARQL query
print("\nExample 4: Sample SPARQL Query Template")
print("-" * 60)
print("""
Here's an example SPARQL query you might use:

File: templates/get_persons.sparql
-----------------------------------
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?name ?email
WHERE {
    ?person rdf:type foaf:Person .
    ?person foaf:name ?name .
    OPTIONAL { ?person foaf:mbox ?email }
}
ORDER BY ?name
LIMIT {{ limit | default(100) }}
-----------------------------------

This template uses Jinja2 syntax ({{ limit | default(100) }}) to allow
customization of the query limit.
""")

# Example 5: Programmatic usage hint
print("\nExample 5: Programmatic Usage (Advanced)")
print("-" * 60)
print("""
For programmatic usage, you can use GraphSource.build():

from sema.query import GraphSource

# Build a graph source (auto-detects type from input)
# GraphSource.build() takes variable arguments (*sources)
source = GraphSource.build("path/to/data.ttl")

# Or from a SPARQL endpoint
source = GraphSource.build("http://endpoint-url")

# You can also pass multiple sources
source = GraphSource.build("file1.ttl", "file2.ttl")

# Then execute queries using the source
result = source.query("SELECT * WHERE { ?s ?p ?o } LIMIT 10")

For detailed API usage, see:
- sema/query/query.py (GraphSource implementation)
- sema/query/__main__.py (CLI implementation)
- sema/query/README.md (module documentation)
""")

print("\n" + "=" * 60)
print("Next Steps:")
print("=" * 60)
print("""
1. Install py-sema: poetry install
2. Prepare your RDF data or SPARQL endpoint URL
3. Try the basic command:
   sema-query --source your_data.ttl --output_format csv
4. Explore template-based queries for reusable patterns
5. Check sema/query/README.md for more details
""")
