# Contributing to py-sema

Thank you for your interest in contributing to py-sema! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Branch and PR Workflow](#branch-and-pr-workflow)

## Getting Started

Before you begin:
1. Check existing [issues](https://github.com/vliz-be-opsci/py-sema/issues) to see if your concern is already addressed
2. For new features or major changes, open an issue first to discuss the proposal
3. Fork the repository and clone it locally

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Poetry (package manager)
- Git (with submodule support)

### Initial Setup

1. **Clone the repository with submodules:**
   ```bash
   git clone --recurse-submodules https://github.com/vliz-be-opsci/py-sema.git
   cd py-sema
   ```

   If you already cloned without submodules:
   ```bash
   git submodule update --init --recursive
   ```

2. **Set up the development environment:**
   
   Using the Makefile (recommended):
   ```bash
   make init-dev
   ```
   
   Or manually with Poetry:
   ```bash
   # Install Poetry if you haven't already
   pip install poetry
   
   # Install all dependencies including dev, test, and docs groups
   poetry install --with dev --with tests --with docs
   ```

3. **Activate the virtual environment:**
   ```bash
   poetry shell
   ```

### Useful Make Targets

The project includes a Makefile with helpful commands:

```bash
make help           # Show all available targets
make init-dev       # Initial development environment setup
make test           # Run the test suite
make test-quick     # Run tests quickly (skips lengthy ones)
make test-coverage  # Run tests with coverage report
make check          # Run linters (black, isort, flake8)
make lint-fix       # Auto-fix linting issues
make clean          # Clean up build artifacts
```

## Code Style

We follow these code style standards:

### Python Code Formatting

- **Line length:** 79 characters (configured in `pyproject.toml`)
- **Formatter:** [Black](https://black.readthedocs.io/)
- **Import sorting:** [isort](https://pycqa.github.io/isort/) (multi-line mode 3 with trailing commas)
- **Linter:** [flake8](https://flake8.pycqa.org/) (ignoring E203, W503)

### Running Code Style Checks

Before submitting a PR, ensure your code passes all style checks:

```bash
# Check code style (does not modify files)
make check

# Automatically fix formatting issues
make lint-fix
```

The `check` target runs:
- `black --check --diff .` - Check code formatting
- `isort --check --diff .` - Check import ordering
- `flake8 .` - Check for code quality issues

### Docstring Convention

- Use descriptive docstrings for all public modules, classes, and functions
- Follow [PEP 257](https://www.python.org/dev/peps/pep-0257/) docstring conventions
- Include:
  - Brief description
  - Parameters (with types)
  - Return values (with types)
  - Exceptions raised (if applicable)

Example:
```python
def process_rdf_data(file_path: str, validate: bool = True) -> dict:
    """
    Process RDF data from a file.
    
    Args:
        file_path: Path to the RDF file
        validate: Whether to validate the data with SHACL
        
    Returns:
        Dictionary containing processed data
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValidationError: If validation fails and validate=True
    """
    # Implementation here
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run tests quickly (skips lengthy tests)
make test-quick

# Run tests with coverage report
make test-coverage

# Run a specific test module (e.g., query, harvest, bench)
make test-module query
```

### Writing Tests

- Place tests in the `tests/` directory, mirroring the structure of `sema/`
- Name test files as `test_*.py`
- Use pytest for writing tests
- Aim for good test coverage (check coverage with `make test-coverage`)
- Include both unit tests and integration tests where appropriate

Example test structure:
```python
import pytest
from sema.query import GraphSource

def test_graph_source_from_file():
    """Test loading RDF data from a file."""
    source = GraphSource("path/to/test/data.ttl")
    assert source is not None
    # Add more assertions
```

### Test Environment Variables

Some tests may require environment variables (e.g., SPARQL endpoint URLs). Check the test files for required variables.

## Submitting Changes

### Before Submitting

1. **Run tests:** Ensure all tests pass (`make test`)
2. **Check code style:** Run `make check` and fix any issues with `make lint-fix`
3. **Update documentation:** If you've changed functionality, update relevant docs
4. **Add tests:** New features should include tests

### Commit Message Guidelines

Write clear, descriptive commit messages:

- Use the imperative mood ("Add feature" not "Added feature")
- First line: brief summary (50 chars or less)
- Blank line, then detailed description if needed
- Reference related issues (e.g., "Fixes #123")

Optional: Use [Conventional Commits](https://www.conventionalcommits.org/) format:
```
feat: add SPARQL query caching
fix: resolve issue with RDF parsing
docs: update installation instructions
test: add tests for harvest module
```

## Branch and PR Workflow

### Creating a Branch

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

3. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

### Opening a Pull Request

1. Go to the [py-sema repository](https://github.com/vliz-be-opsci/py-sema)
2. Click "New Pull Request"
3. Select your branch
4. Fill in the PR template with:
   - **Description:** What changes you made and why
   - **Related Issues:** Link to any related issues
   - **Testing:** How you tested your changes
   - **Checklist:** Confirm you've run tests, linters, etc.

### PR Review Process

- Maintainers will review your PR
- Address any requested changes
- Once approved, a maintainer will merge your PR

## Getting Help

- **Questions?** Open a [discussion](https://github.com/vliz-be-opsci/py-sema/discussions) or issue
- **Found a bug?** Open an [issue](https://github.com/vliz-be-opsci/py-sema/issues)
- **Want to propose a feature?** Open an issue for discussion first

## Code of Conduct

Please be respectful and constructive in all interactions. We are committed to providing a welcoming and inclusive environment for all contributors.

---

Thank you for contributing to py-sema! 🎉
