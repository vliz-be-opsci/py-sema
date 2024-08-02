import pytest
from logging import getLogger
from sema.commons.service import ServiceBase, Trace, TraceMode, ServiceResult, StatusMonitor, RestartException
from random import randint


log = getLogger(__name__)
NUM_CALLS = randint(1, 7)  # at least do things once
NUM_RUNS = randint(2, 7)   # by running at least twice, we force the double-start exception


class CaseResult(ServiceResult, StatusMonitor):
    def __init__(self) -> None:
        self._count = 0

    def inc(self):
        self._count += 1
        log.debug(f"post inc {self._count=}")

    @property
    def success(self):
        return self._count > 0

    @property
    def status(self):
        pass

    def __repr__(self) -> str:
        return f"CaseResult({self._count=})"


def service_factory(mode: TraceMode):
    class CaseService(ServiceBase):
        def __init__(self) -> None:
            self._result = CaseResult()

        @Trace.init(Trace, mode=mode, monitor_attr="_result")
        def process(self) -> CaseResult:
            log.debug(f"process start {self._result=}")
            for i in range(NUM_CALLS):
                self.doit(i)
            return self._result

        @Trace.by(Trace.Event)
        def doit(self, i):
            self._result.inc()
            return i

    return CaseService


@pytest.mark.parametrize(
    "mode, ex_cnt_dist_trace, ex_results, ex_event_sizes, ex_cnt_err",
    [
        (TraceMode.ONCE, 1, [NUM_CALLS], [NUM_CALLS], NUM_RUNS - 1),
        (TraceMode.KEEP, 1, [(i+1)*NUM_CALLS for i in range(NUM_RUNS)], [(i+1)*NUM_CALLS for i in range(NUM_RUNS)], 0),
        (TraceMode.REFRESH, NUM_RUNS, [(i+1)*NUM_CALLS for i in range(NUM_RUNS)], [NUM_CALLS for i in range(NUM_RUNS)], 0),
    ],
)
def test_trace_modes(mode, ex_cnt_dist_trace, ex_results, ex_event_sizes, ex_cnt_err):
    Service = service_factory(mode)
    service = Service()

    trace_instances = set()
    error_count = 0

    for i in range(NUM_RUNS):
        try:
            log.debug(f"test({mode} :: run {i} start")

            result = service.process()
            log.debug(f"test({mode} :: run {i} {result=}")
            assert result.success, f"test({mode} :: run {i} failed"
            assert result._count == ex_results[i], f"test({mode} :: run {i} count mismatch {result._count} != {ex_results[i]}"

            trace = Trace.extract(service)
            log.debug(f"test({mode} :: run {i} {trace=}")
            assert trace is not None, f"test({mode} :: run {i} trace is None"
            assert len(trace._events) == ex_event_sizes[i], f"test({mode} :: run {i} event size mismatch {len(trace._events)} != {ex_event_sizes[i]}"

            trace_instances.add(trace)
            log.debug(f"test({mode} :: run {i} done - {len(trace_instances)=}")
        except RestartException:
            error_count += 1

    assert len(trace_instances) == ex_cnt_dist_trace, f"test({mode} :: distinct trace instances mismatch {len(trace_instances)} != {ex_cnt_dist_trace}"
    assert error_count == ex_cnt_err, f"test({mode} :: error count mismatch {error_count} != {ex_cnt_err}"
