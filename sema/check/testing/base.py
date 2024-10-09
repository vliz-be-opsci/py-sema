# your_submodule/tests/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TestResult:
    success: bool
    error: bool
    message: str
    url: str
    type_test: str


class TestBase(ABC):
    def __init__(self, url: str, type_test: str, options: dict):
        self.url = url
        self.type = type_test
        self.options = options
        self.result = TestResult(
            success=False,
            error=False,
            message="",
            url=url,
            type_test=type_test,
        )

    @abstractmethod
    def run(self) -> TestResult:
        pass
