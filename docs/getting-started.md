# Getting Started

## Installation

### With Poetry

```bash
git clone --recurse-submodules https://github.com/vliz-be-opsci/py-sema.git
cd py-sema
poetry install
```

For development (dev tools, tests, docs):

```bash
poetry install --with dev --with tests --with docs
```

### With pip

```bash
pip install git+https://github.com/vliz-be-opsci/py-sema.git
```

## Quick Commands

```bash
sema-query --help
sema-harvest --help
sema-bench --help
sema-syncfs --help
sema-get --help
```

## Build Documentation

Build static HTML docs:

```bash
make docs-build
```

Start local docs preview server:

```bash
make docs-serve
```
