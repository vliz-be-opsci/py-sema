"""Programmatic runner for the bench-orchestration examples.

This uses the sema.bench `Sembench` service class to execute the same
flows shown in README.md: the default validation + extraction workflow
(`config/sembench.yaml`) and the harvest/validate/query pipeline
(`config/pipeline.yaml`).
"""

from __future__ import annotations

import argparse
import subprocess
import logging
from pathlib import Path
from typing import List

import yaml
from pyshacl import validate

from sema.bench import Sembench


log = logging.getLogger(__name__)


class ExampleBench(Sembench):
    """Lightweight extension that understands the README-style config."""

    def _init_task_configs(self) -> None:
        # Override to keep the original services structure from the README.
        with open(self.sembench_config_path, "r", encoding="utf-8") as yml:
            self.services = yaml.safe_load(yml).get("services", [])
        # Core expects a dict in task_configs; provide a stub to satisfy base init.
        self.task_configs = {}

    def _process(self):
        log.info("Starting bench run with %d service entries", len(self.services))
        for service in self.services:
            kind = service.get("type")
            command = service.get("command")
            name = service.get("name", kind)
            log.info("Running service '%s' (type=%s, command=%s)", name, kind, command)
            if kind == "pyshacl":
                self._run_pyshacl(service)
            elif kind == "custom" and command:
                self._run_command(command, service.get("args", []))
            elif command in {"sema-query", "sema-harvest"}:
                self._run_command(command, service.get("args", []))
            else:
                raise ValueError(
                    f"Unsupported service entry: type={kind} command={command} (from {name})"
                )
            log.info("Finished service '%s'", name)
        self._result._success = True
        log.info("Bench run completed successfully")
        return self._result

    # --- helpers -----------------------------------------------------
    @property
    def _config_dir(self) -> Path:
        return Path(self.sembench_config_path).parent

    def _resolve_path(self, value: str) -> str:
        candidate = (self._config_dir / value).resolve()
        return str(candidate)

    def _resolve_args(self, args: List[str]) -> List[str]:
        resolved = []
        for item in args:
            if item.startswith("-"):
                resolved.append(item)
                continue
            if "/" in item or "\\" in item:
                resolved.append(self._resolve_path(item))
                continue

            candidate = self._config_dir / item
            if candidate.exists():
                resolved.append(str(candidate.resolve()))
            else:
                resolved.append(item)
        return resolved

    def _run_pyshacl(self, service: dict) -> None:
        data_graph = self._resolve_path(service["input"])
        shacl_graph = self._resolve_path(service["shapes"])
        output = service.get("output")

        log.info("SHACL validate data=%s shapes=%s", data_graph, shacl_graph)

        conforms, results_graph, _ = validate(
            data_graph=data_graph,
            shacl_graph=shacl_graph,
            data_graph_format="turtle",
            shacl_graph_format="turtle",
            inference="rdfs",
            debug=False,
        )
        if not conforms:
            raise ValueError("SHACL validation failed")

        if output:
            output_path = Path(self._resolve_path(output))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            results_graph.serialize(destination=output_path, format="turtle")
            log.info("SHACL report written to %s", output_path)
        else:
            log.info("SHACL validation passed (no report output requested)")

    def _run_command(self, command: str, args: List[str]) -> None:
        resolved_args = self._resolve_args(args)
        log.info("Executing command %s with args %s", command, resolved_args)
        if command == "sema-query":
            from sema.query.__main__ import _main as query_main

            query_main(*resolved_args)
        elif command == "sema-harvest":
            from sema.harvest.__main__ import _main as harvest_main

            harvest_main(*resolved_args)
        else:
            # Fallback to shelling out if a future command is added.
            subprocess.run([command, *resolved_args], check=True)
        log.info("Command %s completed", command)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run bench-orchestration examples with Sembench")
    parser.add_argument(
        "--config-name",
        default="sembench.yaml",
        help="Config file inside ./config to run (e.g., sembench.yaml or pipeline.yaml)",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch the config file for changes (delegated to Sembench)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Optional interval seconds for repeated runs (delegated to Sembench)",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first failure (delegated to Sembench)",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    config_dir = Path(__file__).parent / "config"
    config_path = config_dir / args.config_name

    log.info("Using config file: %s", config_path)
    log.info("Options: watch=%s interval=%s fail_fast=%s", args.watch, args.interval, args.fail_fast)

    runner = ExampleBench(
        sembench_config_path=str(config_path),
        sembench_config_file_name=args.config_name,
        scheduler_interval_seconds=args.interval,
        watch_config_file=args.watch,
        fail_fast=args.fail_fast,
    )
    runner.process()


if __name__ == "__main__":
    main()