"""
sema-subyt: Template-Based RDF Generation Examples

This example demonstrates template-based RDF generation from structured data.
"""

print("=" * 70)
print("sema-subyt: Template-Based RDF Generation Examples")
print("=" * 70)

# Example 1: Understanding SubYT
print("\nExample 1: What is sema-subyt?")
print("-" * 70)
print("""
sema-subyt generates RDF triples by applying Jinja2 templates to data:
- Convert CSV/JSON/YAML to RDF
- Template-based transformation
- Support for multiple data sets
- Dynamic output file naming
- Conditional execution
""")

# Example 2: Basic Template
print("\nExample 2: Basic Template Example")
print("-" * 70)
print("""
# Input: persons.csv
id,name,email,age
1,Alice Smith,alice@example.org,30
2,Bob Jones,bob@example.org,25

# Template: person_to_foaf.ttl
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

{% for person in sets._ %}
<http://example.org/person/{{ person.id }}>
    a foaf:Person ;
    foaf:name "{{ person.name }}" ;
    foaf:mbox <mailto:{{ person.email }}> ;
    foaf:age {{ person.age | int }}^^xsd:integer .
{% endfor %}

# Generate RDF
sema-subyt \\
  --name person_to_foaf \\
  --input persons.csv \\
  --output persons.ttl
""")

# Example 3: Using Variables
print("\nExample 3: Template with Variables")
print("-" * 70)
print("""
# Template: dataset.ttl
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

<{{ base_uri }}dataset/{{ year }}>
    a dcat:Dataset ;
    dcterms:title "{{ title }}" ;
    dcterms:issued "{{ year }}-01-01"^^xsd:date .

{% for item in sets._ %}
<{{ base_uri }}item/{{ item.id }}>
    a dcat:Distribution ;
    dcat:dataset <{{ base_uri }}dataset/{{ year }}> ;
    dcterms:title "{{ item.name }}" .
{% endfor %}

# Use template with variables
sema-subyt \\
  --name dataset \\
  --input items.csv \\
  --var base_uri http://example.org/ \\
  --var year 2024 \\
  --var title "Annual Dataset 2024" \\
  --output dataset_2024.ttl
""")

# Example 4: Multiple Data Sets
print("\nExample 4: Multiple Data Sets")
print("-" * 70)
print("""
# Template: integrated.ttl
@prefix org: <http://www.w3.org/ns/org#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

# Organizations
{% for org in sets.organizations %}
<{{ base }}org/{{ org.id }}>
    a org:Organization ;
    org:name "{{ org.name }}" .
{% endfor %}

# Persons linked to organizations
{% for person in sets.persons %}
<{{ base }}person/{{ person.id }}>
    a foaf:Person ;
    foaf:name "{{ person.name }}" ;
    org:memberOf <{{ base }}org/{{ person.org_id }}> .
{% endfor %}

# Generate from multiple sources
sema-subyt \\
  --name integrated \\
  --set persons persons.csv \\
  --set organizations orgs.json \\
  --var base http://example.org/ \\
  --output integrated.ttl
""")

# Example 5: Dynamic Output
print("\nExample 5: Dynamic Output File Naming")
print("-" * 70)
print("""
# Generate one file per record
sema-subyt \\
  --name person_individual \\
  --input persons.csv \\
  --output "output/{id}.ttl"

# With URI template patterns
sema-subyt \\
  --name project_files \\
  --input projects.csv \\
  --output "projects/{year}/{category}/{id}.ttl"
""")

# Example 6: Filtering and Modes
print("\nExample 6: Unique Filtering and Modes")
print("-" * 70)
print("""
# Process only unique records by ID
sema-subyt \\
  --name template \\
  --input data.csv \\
  --unique "{id}" \\
  --output output.ttl

# Non-iterative mode (apply template once to whole dataset)
sema-subyt \\
  --name summary \\
  --input data.csv \\
  --mode no-it \\
  --output summary.ttl

# Conditional execution (only if input changed)
sema-subyt \\
  --name incremental \\
  --input data.csv \\
  --output output.ttl \\
  --conditional
""")

# Example 7: Complete Workflow
print("\nExample 7: Complete Data-to-RDF Workflow")
print("-" * 70)
print("""
# Step 1: Prepare template (templates/catalog.ttl)
# Step 2: Prepare input data (data.csv)
# Step 3: Generate RDF

sema-subyt \\
  --templates /path/to/templates \\
  --name catalog \\
  --input data.csv \\
  --set metadata metadata.json \\
  --var namespace http://example.org/catalog/ \\
  --var created 2024-01-23 \\
  --output "output/{category}/{id}.ttl" \\
  --unique "{id}" \\
  --force

# Step 4: Sync to triple store
sema-syncfs \\
  --root output/ \\
  --base http://example.org/generated/ \\
  --store http://localhost:7200/repositories/kb \\
          http://localhost:7200/repositories/kb/statements

# Step 5: Query the generated data
sema-query \\
  --source http://localhost:7200/repositories/kb \\
  --template_name analysis.sparql
""")

# Example 8: Template Filters
print("\nExample 8: Using Template Filters")
print("-" * 70)
print("""
# Template with type conversion filters
<{{ uri }}>
    foaf:age {{ age | int }}^^xsd:integer ;
    ex:score {{ score | double }}^^xsd:double ;
    ex:active {{ active | bool }}^^xsd:boolean ;
    ex:registered "{{ date | date }}"^^xsd:date ;
    ex:updated "{{ timestamp | datetime }}"^^xsd:dateTime ;
    ex:year {{ year | gyear }}^^xsd:gYear .
""")

print("\n" + "=" * 70)
print("Next Steps:")
print("=" * 70)
print("""
1. Create a templates directory
2. Design your RDF template with Jinja2 syntax
3. Prepare input data (CSV, JSON, YAML)
4. Run: sema-subyt --name <template> --input <data> --output <rdf>
5. Validate generated RDF with rapper or sema-bench
6. See sema/subyt/README.md for detailed documentation
""")
