# sema-roc example assets

This folder provides ready-to-run RO-Crate examples for the ro submodules.
Each example includes a `roc-me.yml` file and a small dataset so you can run the
CLI or the Python API and inspect the generated `ro-crate-metadata.json`.

## Contents
- `basic/`: explicit entries for files, people, and organizations
- `globbed/`: glob-driven crate that auto-includes files and uses `!resolve`

## Quick start
Run these commands from the repository root so the paths line up with the
examples below:

```bash
# Basic explicit example
python -m sema.ro.creator ./examples/ro/basic --force

# Glob-driven example (set env vars first; see below)
python -m sema.ro.creator ./examples/ro/globbed --force --load-os-env
```

You can also use the CLI entrypoint if it is installed in your environment:

```bash
sema-roc ./examples/ro/basic --force
sema-roc ./examples/ro/globbed --force --load-os-env
```

Each run writes `ro-crate-metadata.json` into the example folder you target.

## Example 1: Basic explicit blueprint
The `basic/` crate lists every entity explicitly, which makes it easy to see how
RO-Crate maps to a simple research object.

Highlights:
- Explicit file and dataset entries
- People and organization nodes
- A script declared as `SoftwareSourceCode`

Run:
```bash
python -m sema.ro.creator ./examples/ro/basic --force
```

Key blueprint file: `basic/roc-me.yml`

## Example 2: Glob-driven blueprint with env vars
The `globbed/` crate enables globbing so files and folders are captured without
listing each one manually. It also resolves environment variables with `!resolve`.

Highlights:
- `glob_walk: true` to include all files
- Glob-specific metadata (CSV, Parquet, scripts, workflows)
- `glob_ignore` rules to skip drafts and generated metadata
- Environment variable resolution for dataset title and DOI

Set environment variables (PowerShell):
```powershell
$env:PROJECT_NAME = "Coastal Sensor Campaign"
$env:PROJECT_DOI = "https://doi.org/10.1234/example.2025.1"
$env:AUTHOR_NAME = "Alain Provist"
$env:AUTHOR_EMAIL = "alain.provist@example.org"
```

Set environment variables (bash):
```bash
export PROJECT_NAME="Coastal Sensor Campaign"
export PROJECT_DOI="https://doi.org/10.1234/example.2025.1"
export AUTHOR_NAME="Alain Provist"
export AUTHOR_EMAIL="alain.provist@example.org"
```

Run:
```bash
python -m sema.ro.creator ./examples/ro/globbed --force --load-os-env
```

Key blueprint file: `globbed/roc-me.yml`

## Programmatic usage
You can run the same logic from Python using `ROCreator`:

```python
from sema.ro.creator import ROCreator

creator = ROCreator(
    blueprint_path="./examples/ro/basic/roc-me.yml",
    blueprint_env={},
    rocrate_path="./examples/ro/basic",
    rocrate_metadata_name="ro-crate-metadata.json",
    force=True,
)
creator.process()
```

## Notes and tips
- Only one `roc-*.yml` file can exist per RO-Crate root directory.
- `!resolve` uses Python string formatting, so keys map to env variable names.
- Use `--force` when rerunning to overwrite existing metadata files.
- `glob_ignore` patterns apply to absolute paths; `**/` makes them robust.

See `sema/ro/README.md` for a full CLI reference and RO-Crate background.
