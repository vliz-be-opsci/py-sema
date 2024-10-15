import os
import re
import time
from logging import getLogger
from pathlib import Path
from typing import Dict

import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from sema.bench.dispatcher import TaskDispatcher
from sema.bench.task import Task
from sema.commons.service import ServiceBase, ServiceResult, Trace

log = getLogger(__name__)


class SembenchResult(ServiceResult):
    """Result of the sembench service"""

    def __init__(self) -> None:
        self._success = False

    @property
    def success(self) -> bool:
        return self._success


class ConfigFileEventHandler(FileSystemEventHandler):
    def __init__(self, sembench_config_path, func):
        super().__init__()
        self.sembench_config_path = sembench_config_path
        self.func = func
        os.environ["PYSEMBENCH_WATCHDOG_TIME"] = "0"

    def on_modified(self, event):
        if event.src_path == self.sembench_config_path:
            time_elapsed = time.time() - float(
                os.environ["PYSEMBENCH_WATCHDOG_TIME"]
            )
            if time_elapsed < 2:
                pass
            else:
                try:
                    self.func()
                except Exception as e:
                    raise e
                finally:
                    os.environ["PYSEMBENCH_WATCHDOG_TIME"] = str(time.time())


LOCATION_KEY_PATTERN = r"SEMBENCH_(\w+)_PATH"


def locations_from_environ() -> Dict[str, str]:
    locations = dict()
    for k, v in os.environ.items():
        m = re.match(LOCATION_KEY_PATTERN, k)
        if m:
            locations[m.group(1).lower()] = v
    return locations


class Sembench(ServiceBase):
    def __init__(
        self,
        locations: Dict[str, str] = None,
        sembench_config_path=None,
        sembench_config_file_name=None,
        scheduler_interval_seconds=None,
        watch_config_file=False,
        fail_fast=False,
    ):
        """Create a Sembench object.

        :param locations: dict of keyed paths to various filesystem locations
        with specific roles, such as "home", "input", "output", ...
        Optional; defaults to dict with key "home" derived from the
        sembench_config_path and key "input" same as "home"

        :param sembench_config_path: Path to the sembench config file.
        Optional; defaults to {home}/sembench.yaml.

        :param sembench_config_file_name: Name of the sembench config file.
        Optional; defaults to sembench.yaml.
        """
        locations = locations or dict()
        self.locations = {
            key.lower(): Path(loc) for key, loc in locations.items()
        }

        if sembench_config_path is not None:  # explicit config path
            sembench_config_path = Path(sembench_config_path)
            assert sembench_config_path.exists(), "not found config_path"
            self.sembench_config_path = str(sembench_config_path)
            config_file_name = sembench_config_path.name
            if sembench_config_file_name is not None:
                assert sembench_config_file_name == config_file_name
            self.sembench_config_file_name = config_file_name
            if "home" not in self.locations:
                # get home location from the config_path
                self.locations["home"] = sembench_config_path.parent
        else:
            # reverse logic -- use home to find config_path
            assert "home" in self.locations, "home path required"
            home = self.locations["home"]
            if not sembench_config_file_name:
                sembench_config_file_name = "sembench.yaml"
            sembench_config_path = home / sembench_config_file_name
            assert sembench_config_path.exists(), "not found config_path"
            self.sembench_config_path = str(sembench_config_path)
            self.sembench_config_file_name = sembench_config_path.name

        if "input" not in self.locations:  # take same as home
            self.locations["input"] = self.locations["home"]
        if "output" not in self.locations:  # take same as input
            self.locations["output"] = self.locations["input"]

        self.scheduler_interval_seconds = scheduler_interval_seconds
        self.watch_config_file = watch_config_file
        self.fail_fast = fail_fast

        self.task_configs = None
        self._init_task_configs()
        assert isinstance(self.task_configs, dict)
        self._result = SembenchResult()

    def _init_task_configs(self):
        conf_yml = str(self.sembench_config_path)
        context = {k: str(p) for k, p in self.locations.items()}

        def resolver(
            loader: yaml.SafeLoader, node: yaml.nodes.ScalarNode
        ) -> str:
            txt = loader.construct_scalar(node)
            try:
                txt = txt.format(**context)
            except KeyError as ke:
                log.error(
                    f"config at {conf_yml} contains '{txt}' "
                    f"with unknown key --> {ke}"
                )
            return txt

        loader = yaml.SafeLoader
        loader.add_constructor("!resolve", resolver)

        with open(conf_yml, "r") as yml:
            self.task_configs = yaml.load(yml, Loader=loader)

    def _data_location(self, key):
        input_location = self.locations.get(key)
        return str(input_location) if input_location else None

    @property
    def input_data_location(self):
        return self._data_location("input")

    @property
    def output_data_location(self):
        return self._data_location("output")

    @property
    def sembench_data_location(self):
        return self._data_location("home")

    @staticmethod
    def dispatch_task(task):
        TaskDispatcher().dispatch(task)

    def _process(self):
        tasks = [
            Task(
                input_data_location=self.input_data_location,
                output_data_location=self.output_data_location,
                sembench_data_location=self.sembench_data_location,
                task_id=task_id,
                func=task_config["func"],
                args=task_config["args"],
            )
            for task_id, task_config in self.task_configs.items()
        ]
        for task in tasks:
            try:
                self.dispatch_task(task)
            except Exception as e:
                log.error(f"{task.task_id} failed with exception: {e}")
                if self.fail_fast:
                    raise e

    @Trace.init(Trace)
    def process(self):
        if self.watch_config_file:
            config_file_event_handler = ConfigFileEventHandler(
                self.sembench_config_path,
                self._process,
            )
            observer = Observer()
            observer.schedule(
                event_handler=config_file_event_handler,
                path=self.sembench_data_location,
            )
            observer.start()

            try:
                self._process()
                if self.scheduler_interval_seconds:
                    scheduler = BlockingScheduler()
                    scheduler.add_job(
                        self._process,
                        "interval",
                        seconds=int(self.scheduler_interval_seconds),
                    )
                    scheduler.start()
                    self._result._success = True
                else:
                    while True:
                        pass
            except KeyboardInterrupt:
                observer.stop()
            observer.join()

        else:
            self._process()
            if self.scheduler_interval_seconds:
                scheduler = BlockingScheduler()
                scheduler.add_job(
                    self._process,
                    "interval",
                    seconds=int(self.scheduler_interval_seconds),
                )
                scheduler.start()
                # TODO: technically unreachable code
                # #since the scheduler never stops running
                # check if I can rewrite this to be more clear
                self._result._success = True
