"""
sema-bench Usage Examples

This example demonstrates how to use sema-bench for task orchestration
and SHACL validation.
"""

print("=" * 70)
print("sema-bench: Task Orchestration & SHACL Validation Examples")
print("=" * 70)

# Example 1: Understanding sema-bench
print("\nExample 1: What is sema-bench?")
print("-" * 70)
print("""
sema-bench orchestrates the execution of multiple py-sema services with:
- Scheduled task execution with configurable intervals
- File watching for automatic re-execution on changes
- SHACL validation for RDF data quality
- Fail-fast mode for debugging
- Integration with multiple services
""")

# Example 2: Basic Configuration
print("\nExample 2: Configuration File (sembench.yaml)")
print("-" * 70)
print("""
Create a configuration file defining your services:

# config/sembench.yaml
services:
  - name: validate_persons
    type: pyshacl
    input: data/persons.ttl
    shapes: shapes/person_shape.ttl
    output: reports/person_validation.ttl
    
  - name: extract_data
    type: custom
    command: sema-query
    args:
      - --source
      - data/persons.ttl
      - --template_name
      - extract.sparql
      - --output_location
      - results/extracted.csv
""")

# Example 3: CLI Usage
print("\nExample 3: CLI Usage Examples")
print("-" * 70)
print("""
# Basic validation
sema-bench --config-path ./config

# With custom config file name
sema-bench \\
  --config-path ./config \\
  --config-name validation.yaml

# Continuous monitoring (re-run every 60 seconds)
sema-bench \\
  --config-path ./config \\
  --interval 60 \\
  --watch

# Development mode (fail fast)
sema-bench \\
  --config-path ./config \\
  --fail-fast

# Complete example
sema-bench \\
  --config-path /path/to/config \\
  --config-name sembench.yaml \\
  --interval 500 \\
  --watch \\
  --fail-fast \\
  --logconf logging.yml
""")

# Example 4: Locations mapping
print("\nExample 4: Using Location Mappings")
print("-" * 70)
print("""
Map logical locations to filesystem paths:

sema-bench \\
  --config-path ./config \\
  --locations input /data/input \\
  --locations output /data/output \\
  --locations home /home/user/project

In your config, reference: ${locations.input}/file.ttl
""")

# Example 5: Integration example
print("\nExample 5: Multi-Service Orchestration")
print("-" * 70)
print("""
# config/pipeline.yaml
services:
  # Step 1: Harvest data
  - name: harvest
    command: sema-harvest
    args:
      - --config
      - harvest_config.yaml
      - --dump
      - data/harvested.ttl
      
  # Step 2: Validate harvested data
  - name: validate
    type: pyshacl
    input: data/harvested.ttl
    shapes: shapes/data_shape.ttl
    output: reports/validation.ttl
    depends_on: harvest
    
  # Step 3: Query validated data
  - name: query
    command: sema-query
    args:
      - --source
      - data/harvested.ttl
      - --template_name
      - analysis.sparql
      - --output_location
      - results/analysis.csv
    depends_on: validate

Run with:
sema-bench --config-path config --config-name pipeline.yaml
""")

print("\n" + "=" * 70)
print("Next Steps:")
print("=" * 70)
print("""
1. Create a config directory: mkdir config
2. Create sembench.yaml with your service definitions
3. Run: sema-bench --config-path config
4. For development, add --watch --fail-fast
5. See sema/bench/README.md for detailed documentation
""")
