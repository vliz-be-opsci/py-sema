from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from logging import getLogger
from typing import Dict, Iterable, Sequence

from sema.commons.log import load_log_config

log = getLogger(__name__)


class SemaArgsParser(ArgumentParser):
    """Specific argument parser for the SEMA project.
    Includes a logconf argument to specify the logging configuration file.
    """

    def __init__(self, prog: str, description: str) -> None:
        super().__init__(
            prog=prog,
            description=description,
            formatter_class=ArgumentDefaultsHelpFormatter,
        )
        self.add_logconf_argument()

    def add_logconf_argument(self) -> None:
        self.add_argument(
            "-l",
            "--logconf",
            type=str,
            action="store",
            help="location of the logging config (yml) to use",
        )

    def parse_args(self, args: Sequence[str]) -> Namespace:
        ns: Namespace = super().parse_args(args)
        log.debug(f"{self.prog} called with {args=}")
        load_log_config(ns.logconf)
        log.debug(f"{self.prog} parsed args {ns=}")
        return ns

    @staticmethod
    def args_to_dict(multi_args: Iterable[Iterable[str]]) -> Dict[str, str]:
        """Converts a list of lists of strings to a dictionary."""
        return {k: v for [k, v] in multi_args} if multi_args else {}
