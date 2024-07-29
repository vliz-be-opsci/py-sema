# Service pattern

## What
The external / public services in this sema package all follow a similar pattern.

## Why
This allows us to:
* apply similar `__main__` approach
* make the `main()` testable 
* easily orchestrate these services through yml config files in `sema.bench` 
* have a common approach to auditing and provenance
* streamline the shared knowledge and assistance within the team

## How
The essential parts of this approach are

1. provide a `sema/xyz/service.py` with a subclass implementation of ServiceBase
2. provide a `__main__.py` with a `main(*args_list)` called when `__name__ = '__main__'` with `*sys.argv[:1]`
3. provide a `test_main_cli.py` that at least once builds a `cli_line: str` to be passed into `main(cli_line.split(' '))`