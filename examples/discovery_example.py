"""
sema-get (Discovery) Usage Examples

This example demonstrates how to use sema-get for RDF discovery.
"""

print("=" * 70)
print("sema-get: RDF Discovery Examples")
print("=" * 70)

# Example 1: Understanding Discovery
print("\nExample 1: What is RDF Discovery?")
print("-" * 70)
print("""
sema-get discovers RDF data associated with a subject URI using:
- Content negotiation
- Link following (rdfs:seeAlso, owl:sameAs)
- Well-known locations
- VoID descriptions
- Semantic sitemaps
""")

# Example 2: Basic Discovery
print("\nExample 2: Basic Discovery")
print("-" * 70)
print("""
# Discover and display to stdout
sema-get https://example.org/resource/123 --output -

# Save to file
sema-get https://example.org/resource/123 --output discovered.ttl

# Specify output format
sema-get https://example.org/person/alice \\
  --output alice.jsonld \\
  --format json-ld
""")

# Example 3: Content Negotiation
print("\nExample 3: Content Negotiation")
print("-" * 70)
print("""
# Request specific MIME types
sema-get https://example.org/resource/123 \\
  --request-mimes text/turtle,application/rdf+xml

# Multiple MIME types (try in order)
sema-get https://dbpedia.org/resource/Python \\
  --request-mimes text/turtle \\
  --request-mimes application/rdf+xml \\
  --request-mimes application/ld+json \\
  --output python.ttl
""")

# Example 4: Triple Store Integration
print("\nExample 4: Store in Triple Store")
print("-" * 70)
print("""
# Discover and store in named graph
sema-get https://example.org/resource/123 \\
  --read-uri http://localhost:7200/repositories/myrepo \\
  --write-uri http://localhost:7200/repositories/myrepo/statements \\
  --graph http://example.org/discovered/resource123

# Query the discovered data
sema-query \\
  --source http://localhost:7200/repositories/myrepo \\
  --template_name analysis.sparql
""")

# Example 5: Discovery Tracing
print("\nExample 5: Discovery Tracing")
print("-" * 70)
print("""
# Enable tracing for debugging
sema-get https://example.org/resource/123 \\
  --output discovered.ttl \\
  --trace logs/discovery_trace.txt

The trace file will show:
- Attempted discovery techniques
- HTTP requests and responses  
- Found URIs and their sources
- Success/failure of each technique
""")

# Example 6: Practical Examples
print("\nExample 6: Practical Use Cases")
print("-" * 70)
print("""
# Discover DBpedia resource
sema-get https://dbpedia.org/resource/Python_(programming_language) \\
  --output dbpedia_python.ttl

# Discover with zero-result tolerance (don't fail if empty)
sema-get https://example.org/maybe-exists \\
  --accept-zero \\
  --output result.ttl

# Bulk discovery
for uri in $(cat resource_uris.txt); do
  filename=$(echo $uri | md5sum | cut -d' ' -f1)
  sema-get "$uri" --output "discovered/$filename.ttl"
done

# Discover then query
sema-get https://example.org/dataset \\
  --output temp_discovered.ttl

sema-query \\
  --source temp_discovered.ttl \\
  --template_name extract.sparql \\
  --output_location results.csv
""")

# Example 7: Complete Example
print("\nExample 7: Complete Discovery Workflow")
print("-" * 70)
print("""
sema-get https://example.org/person/alice \\
  --request-mimes text/turtle,application/ld+json \\
  --output discovered/alice.ttl \\
  --format turtle \\
  --read-uri http://localhost:7200/repositories/kb \\
  --write-uri http://localhost:7200/repositories/kb/statements \\
  --graph http://example.org/discovered/alice \\
  --trace logs/alice_discovery.txt \\
  --logconf logging.yml
""")

print("\n" + "=" * 70)
print("Next Steps:")
print("=" * 70)
print("""
1. Identify URIs to discover
2. Test discovery: sema-get <uri> --output test.ttl
3. Enable tracing for debugging: --trace discovery.log
4. Integrate with other services (query, harvest, etc.)
5. See sema/discovery/README.md for detailed documentation
""")
