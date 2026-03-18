# RO Examples

Canonical source README:
<https://github.com/vliz-be-opsci/py-sema/blob/main/examples/ro/README.md>

## What this example covers

- Generate RO-Crate metadata from `roc-me.yml` blueprints.
- Compare explicit-entry and glob-driven crate styles.
- Resolve environment variables for metadata fields.

## Key assets

- Basic crate: `examples/ro/basic/`
- Globbed crate: `examples/ro/globbed/`
- Blueprints: `examples/ro/basic/roc-me.yml`, `examples/ro/globbed/roc-me.yml`

## Quick start

```bash
python -m sema.ro.creator ./examples/ro/basic --force
python -m sema.ro.creator ./examples/ro/globbed --force --load-os-env
```

## Optional CLI form

```bash
sema-roc ./examples/ro/basic --force
sema-roc ./examples/ro/globbed --force --load-os-env
```

## Notes

- One `roc-*.yml` file is expected per RO-Crate root.
- Use `--force` when rerunning and replacing metadata output.
