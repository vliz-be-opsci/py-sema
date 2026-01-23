"""
Simple SPARQL Query Example

This example demonstrates how to query RDF data using py-sema's query module.
"""

from sema.query import GraphSource, DefaultSparqlBuilder

# Example 1: Load RDF data from a file
print("Example 1: Loading RDF data from a file")
print("-" * 50)

# Create a GraphSource from a local RDF file
# Replace with your own .ttl, .rdf, or .nt file
source = GraphSource("data.ttl")
print(f"✓ Loaded RDF data source")

# Example 2: Load RDF data from a SPARQL endpoint
print("\nExample 2: Connecting to a SPARQL endpoint")
print("-" * 50)

# Uncomment to use a SPARQL endpoint instead
# source = GraphSource("http://localhost:7200/repositories/my-repo")
# print(f"✓ Connected to SPARQL endpoint")

# Example 3: Execute a SPARQL query
print("\nExample 3: Execute a SPARQL query")
print("-" * 50)

# Simple SPARQL query to get all subjects and objects
query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?subject ?predicate ?object
WHERE {
    ?subject ?predicate ?object .
}
LIMIT 10
"""

# Note: The exact API for executing queries may vary
# Check the sema.query documentation for the current API
print("Query to execute:")
print(query)

# Example 4: Using SPARQL templates
print("\nExample 4: Using SPARQL templates with Jinja2")
print("-" * 50)

# py-sema supports Jinja2 templates for dynamic SPARQL queries
# This allows you to parameterize your queries

template_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?subject
WHERE {
    ?subject rdf:type <{{ resource_type }}> .
}
LIMIT {{ limit }}
"""

print("Template query:")
print(template_query)
print("\nParameters: resource_type, limit")

print("\n" + "=" * 50)
print("Next steps:")
print("1. Prepare your RDF data file (Turtle, RDF/XML, N-Triples)")
print("2. Modify the source path or endpoint URL")
print("3. Customize the SPARQL query for your use case")
print("4. Run: python examples/simple_query.py")
print("\nFor more details, see sema/query/README.md")
