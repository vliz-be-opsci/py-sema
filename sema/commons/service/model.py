from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable
from datetime import datetime
from logging import getLogger


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
    @property
    @abstractmethod
    def status(self):
        pass


class RestartException(Exception):
    """Exception to be raised when a service is attempted to be restarted."""
    def __init__(self, service_name: str):
        super().__init__(f"Service {service_name} is already running")


class TraceMode(Enum):
    """Enumeration of the possible modes for the trace initialization."""
    ONCE = "once"
    """allow to initialize the trace oject only once - on second call it will raise an exception"""
    KEEP = "keep"
    """allow to keep the existing trace object, if any - on second call it will not create a new one"""
    REFRESH = "refresh"
    """force to create a new trace object on every call, even if there is already one"""


class Trace():
    """Helper class to trace the execution of a service.
        Its instances are keeping track of the events that happened 
        during the service execution.
        Furthermore it provides decorators and staticmethods to assist 
        mixing in the tracing functionality into any specific service. """
    def __init__(self, monitor: StatusMonitor) -> None:
        """Initializes the trace.
            Typically @Trace.init decorator will be automatically 
            calling this constructor, as well as being responsible for
            discovering the monitor to apply. """
        self._events = list()
        self._monitor = monitor

    def add_event(self, event):
        status = self._monitor.status if self._monitor else None
        self._events.append(dict(event=event, status=status, ts=datetime.now()))

    class Event():
        def __init__(self, _trace_name, _trace_return=None, *args, **kwargs):
            self.name = _trace_name
            self.returns = _trace_return
            self.listargs = args
            self.dictargs = kwargs

        def __repr__(self) -> str:
            return f"Trace.Event of {self.name} ( {self.listargs}, {self.dictargs} ) -> {self.returns}"

    @staticmethod
    def by(evt_cls: type):
        """decorator factory, parametrized by the event-class to be added to the Trace.
        :param evt_cls: the class of the event to be added to the trace.
        """
        assert isinstance(evt_cls, type), "evt_cls must be a type"
        # TODO we might want to lower this next requirement
        assert issubclass(evt_cls, Trace.Event), "evt_cls must be a subclass of Trace.Event"
        log.debug(f"decorator Trace.by for {evt_cls.__name__}")

        def by_wrapper(fn: Callable):
            """actual decorator, returnig the wrapped function being traced.
            :param fn: the function to be wrapped and traced.
            """
            assert isinstance(fn, Callable), "fn must be a callable"
            log.debug(f"decorator Trace.by wrapper for {fn.__name__} with {evt_cls.__name__}")

            def wrapped_by(target, *args, **kwargs):
                """actual wrapper, calling the function and adding the event to the trace."""
                resp = fn(target, *args, **kwargs)
                target._trace.add_event(evt_cls(fn.__name__, resp, *args, **kwargs))
                return resp
            return wrapped_by
        return by_wrapper

    @staticmethod
    def init(trc_cls: type, *, mode: TraceMode = TraceMode.ONCE, monitor_attr: str = None):
        """decorator factory, parametrized by the Trace-class to be used.
        :param trc_cls: the class of the Trace to be used
        :param mode: the mode of the trace initialization
        :param monitor_attr: the name of the attribute to be used as the monitor
        """
        assert isinstance(trc_cls, type), "trc_cls must be a type"
        log.debug(f"decorator Trace.init for {trc_cls.__name__}")

        def init_wrapper(fn: Callable):
            """actual decorator, returnig the wrapped function that initializes the trace.
            :param fn: the function to be wrapped and initializing the trace."""
            assert isinstance(fn, Callable), "fn must be a callable"
            log.debug(f"decorator Trace.init wrapper for {fn.__name__} with {trc_cls.__name__}")

            def wrapped_init(target, *args, **kwargs):
                """"""
                if mode == TraceMode.ONCE:
                    # we should not re-enter this method
                    if hasattr(target, "_trace"):
                        raise RestartException(type(target).__name__)
                if mode != TraceMode.KEEP or not hasattr(target, "_trace"):
                    # only make trace if there is none or if we cannot keep the existing one
                    monitor = getattr(target, monitor_attr, None) if monitor_attr else None
                    if monitor is None and isinstance(target, StatusMonitor):
                        monitor = target
                    assert (
                        monitor is None or isinstance(monitor, StatusMonitor)
                    ), f"{type(monitor).__name__} not a proper StatusMonitor"
                    target._trace = trc_cls(monitor)
                resp = fn(target, *args, **kwargs)
                print(f"end tracer.init {resp=}")
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
