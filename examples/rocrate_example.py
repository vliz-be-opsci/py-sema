"""
sema-roc: RO-Crate Creator Examples

This example demonstrates RO-Crate metadata generation.
"""

print("=" * 70)
print("sema-roc: RO-Crate Creator Examples")
print("=" * 70)

# Example 1: Understanding RO-Crate
print("\nExample 1: What is RO-Crate?")
print("-" * 70)
print("""
RO-Crate (Research Object Crate) is a standard for packaging research data:
- Machine-readable metadata in JSON-LD
- Based on schema.org vocabulary
- Links data, code, workflows, and documentation
- Supports FAIR principles (Findable, Accessible, Interoperable, Reusable)

sema-roc generates ro-crate-metadata.json from YAML configurations.
""")

# Example 2: Basic Configuration
print("\nExample 2: Basic RO-Crate Configuration")
print("-" * 70)
print("""
Create roc-me.yml in your research object directory:

# roc-me.yml
"@context": "https://w3id.org/ro/crate/1.1/context"
"@graph":
  # Metadata descriptor
  - "@id": "ro-crate-metadata.json"
    "@type": "CreativeWork"
    conformsTo:
      "@id": "https://w3id.org/ro/crate/1.1"
    about:
      "@id": "./"
      
  # Root dataset
  - "@id": "./"
    "@type": "Dataset"
    name: "My Research Dataset"
    description: "Description of research"
    datePublished: "2024-01-23"
    license:
      "@id": "https://creativecommons.org/licenses/by/4.0/"
    author:
      - "@id": "#researcher1"
      
  # Author
  - "@id": "#researcher1"
    "@type": "Person"
    name: "Jane Researcher"
    email: "jane@example.org"
    affiliation:
      "@id": "https://ror.org/example"

Generate metadata:
sema-roc
""")

# Example 3: CLI Usage
print("\nExample 3: CLI Usage Examples")
print("-" * 70)
print("""
# Create in current directory
sema-roc

# Specify RO-Crate root directory
sema-roc /path/to/rocrate

# Custom output filename
sema-roc . metadata.json

# Force overwrite existing file
sema-roc --force

# Complete example
sema-roc \\
  /path/to/my-rocrate \\
  custom-metadata.json \\
  --force \\
  --load-os-env \\
  --logconf logging.yml
""")

# Example 4: Environment Variables
print("\nExample 4: Using Environment Variables")
print("-" * 70)
print("""
# roc-me.yml with environment variables
"@graph":
  - "@id": "./"
    "@type": "Dataset"
    name: !resolve "${PROJECT_NAME}"
    version: !resolve "${VERSION}"
    author:
      name: !resolve "${AUTHOR_NAME}"
      email: !resolve "${AUTHOR_EMAIL}"

# Set environment variables
export PROJECT_NAME="My Research Project"
export VERSION="1.0.0"
export AUTHOR_NAME="Jane Doe"
export AUTHOR_EMAIL="jane@example.org"

# Generate with environment variable resolution
sema-roc --load-os-env
""")

# Example 5: Research Dataset Example
print("\nExample 5: Complete Research Dataset")
print("-" * 70)
print("""
# roc-me.yml for research dataset
"@context": "https://w3id.org/ro/crate/1.1/context"
"@graph":
  - "@id": "ro-crate-metadata.json"
    "@type": "CreativeWork"
    conformsTo:
      "@id": "https://w3id.org/ro/crate/1.1"
    about:
      "@id": "./"
      
  - "@id": "./"
    "@type": "Dataset"
    name: "Climate Model Results 2024"
    description: "High-resolution climate model output for 2024"
    datePublished: "2024-01-23"
    license:
      "@id": "https://creativecommons.org/licenses/by/4.0/"
    author:
      - "@id": "https://orcid.org/0000-0002-1825-0097"
    hasPart:
      - "@id": "data/temperature.csv"
      - "@id": "data/precipitation.csv"
      - "@id": "scripts/analysis.py"
      
  - "@id": "https://orcid.org/0000-0002-1825-0097"
    "@type": "Person"
    name: "Dr. Alice Climate"
    email: "alice@climate.edu"
    affiliation:
      "@id": "https://ror.org/05kdjqf72"
      
  - "@id": "data/temperature.csv"
    "@type": "File"
    name: "Temperature Data"
    description: "Daily temperature readings"
    encodingFormat: "text/csv"
    contentSize: "5242880"
    
  - "@id": "data/precipitation.csv"
    "@type": "File"
    name: "Precipitation Data"
    description: "Daily precipitation measurements"
    encodingFormat: "text/csv"
    
  - "@id": "scripts/analysis.py"
    "@type": ["File", "SoftwareSourceCode"]
    name: "Analysis Script"
    programmingLanguage: "Python"
""")

# Example 6: Computational Workflow
print("\nExample 6: Computational Workflow Package")
print("-" * 70)
print("""
# roc-me.yml for workflow
"@graph":
  - "@id": "./"
    "@type": "Dataset"
    name: "Bioinformatics Pipeline"
    description: "RNA-seq analysis workflow"
    mainEntity:
      "@id": "workflow.cwl"
      
  - "@id": "workflow.cwl"
    "@type": ["File", "ComputationalWorkflow"]
    name: "RNA-seq Analysis Workflow"
    programmingLanguage:
      "@id": "https://w3id.org/workflowhub/workflow-ro-crate#cwl"
    input:
      - "@id": "#input1"
    output:
      - "@id": "#output1"
      
  - "@id": "#input1"
    "@type": "FormalParameter"
    name: "fastq_files"
    description: "Input FASTQ files"
    
  - "@id": "#output1"
    "@type": "FormalParameter"
    name: "counts_matrix"
    description: "Gene expression counts"
""")

# Example 7: Integration Workflow
print("\nExample 7: Complete Research Workflow")
print("-" * 70)
print("""
# 1. Organize research object
mkdir -p my-research/{data,scripts,docs}

# 2. Add research artifacts
cp dataset.csv my-research/data/
cp analysis.py my-research/scripts/
cp README.md my-research/docs/

# 3. Create RO-Crate configuration
cat > my-research/roc-me.yml << 'EOF'
"@context": "https://w3id.org/ro/crate/1.1/context"
"@graph":
  - "@id": "ro-crate-metadata.json"
    "@type": "CreativeWork"
    conformsTo:
      "@id": "https://w3id.org/ro/crate/1.1"
    about:
      "@id": "./"
  - "@id": "./"
    "@type": "Dataset"
    name: "My Research"
    description: "Research project description"
    hasPart:
      - "@id": "data/dataset.csv"
      - "@id": "scripts/analysis.py"
EOF

# 4. Generate RO-Crate metadata
cd my-research
sema-roc --force

# 5. Validate (if validation tools available)
# rocrate validate ro-crate-metadata.json

# 6. Package for publication
zip -r ../my-research-rocrate.zip .
""")

# Example 8: Directory Structure
print("\nExample 8: RO-Crate Directory Structure")
print("-" * 70)
print("""
Recommended structure for RO-Crate:

my-rocrate/
├── roc-me.yml                # Configuration (input)
├── ro-crate-metadata.json    # Generated metadata (output)
├── README.md                 # Human-readable description
├── LICENSE                   # License file
├── data/                     # Research data
│   ├── raw/
│   │   └── experiment.csv
│   └── processed/
│       └── results.csv
├── scripts/                  # Analysis code
│   ├── preprocess.py
│   └── analyze.py
├── workflows/                # Computational workflows (if any)
│   └── pipeline.cwl
└── docs/                     # Documentation
    ├── methods.md
    └── results.md

All referenced files should exist before creating metadata.
""")

print("\n" + "=" * 70)
print("Next Steps:")
print("=" * 70)
print("""
1. Organize your research artifacts in a directory
2. Create roc-me.yml with metadata describing your research
3. Run: sema-roc
4. Review generated ro-crate-metadata.json
5. Validate with RO-Crate tools if available
6. Package and share your research object
7. See sema/ro/README.md for detailed documentation
8. Learn more: https://www.researchobject.org/ro-crate/
""")
