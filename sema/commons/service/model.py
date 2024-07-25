from abc import ABC, abstractmethod
from typing import Tuple


class ServiceResult(ABC):
    @property
    @abstractmethod
    def success(self) -> bool:
        """ indicates the execution of the service was succesful """
        pass  # pragma: no cover

    def __bool__(self) -> bool:
        return self.success


class ServiceTrace(ABC):
    @abstractmethod
    def toProv(self):  # todo consider return tyupe from sema.commons.prov
        """converts the trace to a PROV document"""
        pass  # pragma: no cover


class ServiceBase(ABC):
    @abstractmethod
    def process(self) -> Tuple[ServiceResult, ServiceTrace]:
        """ executes the service command
        :return: a tuple of the result and the trace
        :rtype: Tuple[ServiceResult, ServiceTrace]
        """
        pass  # pragma: no cover
