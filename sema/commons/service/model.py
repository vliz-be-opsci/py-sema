from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from logging import getLogger
from typing import Any, Callable

log = getLogger(__name__)


class ServiceResult(ABC):
    """The base for any specific result of a specific service execution"""

    @property
    @abstractmethod
    def success(self) -> bool:
        """indicates the execution of the service was succesful"""
        pass  # pragma: no cover

    def __bool__(self) -> bool:
        """ensures the result can be used as a boolean"""
        return self.success


class StatusMonitor(ABC):
    """Interface defining a status monitor.
    Should be implemented by any class that should be monitored
    throughout the tracing of the service execution.
    Typically this would be the service itself, or the service-result."""

    def __init__(self):
        self._trace = None

    @property
    @abstractmethod
    def status(self) -> Any:
        pass


class RestartException(Exception):
    """Exception to be raised when a service is attempted to be restarted."""

    def __init__(self, service_name: str):
        super().__init__(f"Service {service_name} is already running")


class TraceMode(Enum):
    """Enumeration of the possible modes for the trace initialization."""

    ONCE = "once"
    """do not allow multiple calls, but throw RestartException in stead"""
    KEEP = "keep"
    """allow multiple calls, reuse the trace object for each"""
    REFRESH = "refresh"
    """allow multiple calls, create a new trace object for each"""


class Trace:
    """Helper class to trace the execution of a service.
    Its instances are keeping track of the events that happened
    during the service execution.
    Furthermore it provides decorators and staticmethods to assist
    mixing in the tracing functionality into any specific service."""

    def __init__(self, monitor: StatusMonitor) -> None:
        """Initializes the trace.
        Typically @Trace.init decorator will be automatically
        calling this constructor, as well as being responsible for
        discovering the monitor to apply."""
        self._events = list()
        self._monitor = monitor

    def add_event(self, event):
        status = self._monitor.status if self._monitor else None
        self._events.append(
            dict(event=event, status=status, ts=datetime.now())
        )

    class Event:
        def __init__(self, _trace_name, _trace_return=None, *args, **kwargs):
            self.name = _trace_name
            self.returns = _trace_return
            self.listargs = args
            self.dictargs = kwargs

        def __repr__(self) -> str:
            return (
                f"Trace.Event :: {self.name} "
                f"( {self.listargs}, {self.dictargs} ) -> {self.returns}"
            )

    @property
    def events(self):
        return self._events

    @staticmethod
    def by(evt_cls: type, name: str | None = None):
        """decorator factory, uses the passed event-class
        to be applied in the decoration of the function-call
        :param evt_cls: the class of the event to be added to the trace.
        """
        assert isinstance(evt_cls, type), "evt_cls must be a type"
        # TODO we might want to lower this next requirement
        assert issubclass(
            evt_cls, Trace.Event
        ), "evt_cls must be a subclass of Trace.Event"
        log.debug(f"decorator Trace.by for {evt_cls.__name__}")

        def by_wrapper(fn: Callable):
            """actual decorator, returnig the wrapped function being traced.
            :param fn: the function to be wrapped and traced.
            """
            assert isinstance(fn, Callable), "fn must be a callable"
            evtname = name or fn.__name__
            log.debug(
                f"decorator Trace.by wrapper for {fn.__name__} as {evtname}"
                f"with {evt_cls.__name__}"
            )

            def wrapped_by(target, *args, **kwargs):
                """actual wrapper, just calling the function it wraps
                while adding the call + return + arguments as an
                event to the trace."""
                resp = fn(target, *args, **kwargs)
                target._trace.add_event(
                    evt_cls(evtname, resp, *args, **kwargs)
                )
                return resp

            return wrapped_by

        return by_wrapper

    @staticmethod
    def init(
        trc_cls: type,
        *,
        mode: TraceMode = TraceMode.ONCE,
        monitor_attr: str | None = None,
    ):
        """decorator factory, parametrized by the Trace-class to be used.
        :param trc_cls: the class of the Trace to be used
        :param mode: the mode of the trace initialization
        :param monitor_attr: attribute name pointing to the monitor
            can be None to use the containing object itself
            targetted object needs to be of type StatusMonitor
        """
        assert isinstance(trc_cls, type), "trc_cls must be a type"
        log.debug(f"decorator Trace.init for {trc_cls.__name__}")

        def init_wrapper(fn: Callable):
            """actual decorator, wraps the function to initializes the trace.
            :param fn: the function to be wrapped and initializing the trace.
            """
            assert isinstance(fn, Callable), "fn must be a callable"
            log.debug(
                f"decorator Trace.init wrapper for {fn.__name__} "
                f"with {trc_cls.__name__}"
            )

            def wrapped_init(target, *args, **kwargs):
                """"""
                if mode == TraceMode.ONCE:
                    # we should not re-enter this method
                    if hasattr(target, "_trace"):
                        raise RestartException(type(target).__name__)
                if mode != TraceMode.KEEP or not hasattr(target, "_trace"):
                    # new trace only if there is none or we should not keep
                    monitor = (
                        getattr(target, monitor_attr, None)
                        if monitor_attr
                        else None
                    )
                    if monitor is None and isinstance(target, StatusMonitor):
                        monitor = target
                    assert monitor is None or isinstance(
                        monitor, StatusMonitor
                    ), f"{type(monitor).__name__} not a proper StatusMonitor"
                    target._trace = trc_cls(monitor)
                resp = fn(target, *args, **kwargs)
                return resp

            return wrapped_init

        return init_wrapper

    @staticmethod
    def extract(target):
        return getattr(target, "_trace")

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._events})"


class ServiceBase(ABC):
    @abstractmethod
    def process(self) -> ServiceResult:
        """executes the service command
        :return: the result
        :rtype: ServiceResult
        """
        pass  # pragma: no cover
