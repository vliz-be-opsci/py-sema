# sema-bench: Task Orchestration and SHACL Validation

`sema-bench` is a task orchestration tool that manages the execution of multiple py-sema services with SHACL validation capabilities.

## Overview

Bench orchestrates service execution using configuration files, with support for:
- Scheduled task execution with configurable intervals
- File watching for automatic re-execution on configuration changes
- SHACL validation for RDF data quality assurance
- Fail-fast mode for quick debugging
- Integration with multiple py-sema services

## Installation

```bash
poetry install
# Or for development
poetry install --with dev --with tests
```

## Command-Line Usage

```bash
sema-bench --config-path <path> [options]
```

### Required Arguments

- `-c, --config-path CONFIG_PATH`: Path to the sembench configuration parent folder (required)

### Optional Arguments

- `-n, --config-name CONFIG_NAME`: Name of the sembench config file (default: `sembench.yaml`)
- `--interval INTERVAL`: Interval in seconds to run the scheduler (default: 1000)
- `-w, --watch`: Watch the config file for changes and re-execute automatically
- `-ff, --fail-fast`: Fail fast if any service fails (useful for debugging)
- `-l, --logconf LOGCONF`: Path to logging configuration file (YAML format)
- `-loc, --locations KEY PATH`: Dict of keyed paths to filesystem locations (e.g., 'home', 'input', 'output')

## Configuration File Format

Create a `sembench.yaml` file with your service configurations:

```yaml
# Example sembench.yaml
services:
  - name: validate_data
    type: pyshacl
    input: data/input.ttl
    shapes: shapes/data_shape.ttl
    output: data/validation_report.ttl
    
  - name: process_data
    type: custom
    command: sema-query
    args:
      - --source
      - data/input.ttl
      - --template_name
      - process.sparql
```

## Usage Examples

### Basic Validation

Run SHACL validation once with a configuration:

```bash
sema-bench --config-path ./config --config-name validation.yaml
```

### Continuous Monitoring

Watch configuration files and re-run on changes:

```bash
sema-bench --config-path ./config --watch --interval 60
```

### Fail-Fast Development Mode

Stop immediately on first error for debugging:

```bash
sema-bench --config-path ./config --fail-fast
```

### With Custom Logging

```bash
sema-bench --config-path ./config --logconf logging.yml
```

### Complete Example

```bash
sema-bench \
  --config-path /path/to/config \
  --config-name sembench.yaml \
  --interval 500 \
  --watch \
  --fail-fast \
  --logconf logging.yml
```

## Programmatic Usage

```python
from sema.bench import Sembench

# Initialize with configuration
bench = Sembench(
    sembench_config_path="/path/to/config",
    sembench_config_file_name="sembench.yaml"
)

# Run the orchestration
bench.run()
```

## Integration with Other Services

sema-bench can orchestrate any py-sema service:
- `sema-query`: SPARQL query execution
- `sema-harvest`: RDF data harvesting
- `sema-subyt`: Template-based triple generation
- `sema-syncfs`: Filesystem synchronization
- Custom services via configuration

## Best Practices

1. **Use fail-fast during development** to quickly identify configuration issues
2. **Set appropriate intervals** for scheduled tasks to balance responsiveness and resource usage
3. **Enable watching** for configuration files in development environments
4. **Use custom locations** (`-loc`) to make configurations portable across environments
5. **Configure logging** to track orchestration execution and debug issues

## Related Modules

- [SHACL Handler](../commons/pyshacl/) - SHACL validation implementation
- [Service Framework](../commons/service/) - Base service architecture
- [Task Dispatcher](./dispatcher.py) - Task execution management

## See Also

- Test files: `tests/bench/` for usage examples
- Configuration examples: `tests/bench/resources/`