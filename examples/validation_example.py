"""
SHACL Validation Example

This example demonstrates how to validate RDF data using SHACL shapes
with py-sema's bench module.
"""

print("SHACL Validation Example")
print("=" * 50)

# Example 1: Understanding SHACL validation
print("\nExample 1: What is SHACL Validation?")
print("-" * 50)
print("""
SHACL (Shapes Constraint Language) is used to validate RDF data:
- Define constraints on your data structure
- Ensure data quality and consistency
- Validate before storing or publishing data
- Generate validation reports

py-sema's bench module provides SHACL validation capabilities.
""")

# Example 2: Using the sema-bench CLI
print("\nExample 2: Using the sema-bench CLI")
print("-" * 50)
print("""
The sema-bench command-line tool validates RDF data:

    sema-bench --help

Example usage:
    # Validate RDF data against SHACL shapes
    sema-bench --data my_data.ttl --shapes my_shapes.ttl
    
Run 'sema-bench --help' for all available options.
""")

# Example 3: SHACL shape example
print("\nExample 3: Sample SHACL Shape")
print("-" * 50)
print("""
Example SHACL shape (save as shapes.ttl):

@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .

ex:PersonShape
    a sh:NodeShape ;
    sh:targetClass ex:Person ;
    sh:property [
        sh:path ex:name ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
    ] ;
    sh:property [
        sh:path ex:age ;
        sh:datatype xsd:integer ;
        sh:minInclusive 0 ;
    ] .

This shape ensures that:
- All ex:Person instances must have a name (string)
- Age must be a non-negative integer if present
""")

# Example 4: Sample RDF data
print("\nExample 4: Sample RDF Data to Validate")
print("-" * 50)
print("""
Valid data example (save as data_valid.ttl):

@prefix ex: <http://example.org/> .

ex:john
    a ex:Person ;
    ex:name "John Doe" ;
    ex:age 30 .

Invalid data example (save as data_invalid.ttl):

@prefix ex: <http://example.org/> .

ex:jane
    a ex:Person ;
    ex:age -5 .  # Missing required name, negative age

""")

# Example 5: Validation workflow
print("\nExample 5: Validation Workflow")
print("-" * 50)
print("""
1. Create your SHACL shapes (constraints)
2. Prepare your RDF data
3. Run validation:
   sema-bench --data data.ttl --shapes shapes.ttl
4. Review the validation report
5. Fix any violations
6. Re-validate until clean
""")

print("\n" + "=" * 50)
print("Next steps:")
print("1. Review sema/bench/README.md for module details")
print("2. Check test files in tests/bench/ for real examples")
print("3. Run 'sema-bench --help' for CLI options")
print("4. Learn more about SHACL: https://www.w3.org/TR/shacl/")
