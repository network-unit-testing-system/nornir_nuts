import inspect
from typing import List, Dict, Tuple, FrozenSet, Optional, Any
from types import ModuleType
from concurrent.futures import ThreadPoolExecutor

from nornir.core.task import AggregatedResult, Task, MultiResult
from nornir.core.inventory import Host


class CachedThreadedRunner:
    """
    CachedThreadedRunner returns cached result or runs the task over each host using threads.
    CachedThreadedRunner is an updated version of the Nornir ThreadedRunner

    Arguments:
        num_workers: number of threads to use
    """

    CACHE: Dict[
        Tuple[Tuple[FrozenSet[Tuple[str, Any]], bool, str, Optional[ModuleType]], str],
        MultiResult,
    ] = dict()

    def __init__(self, num_workers: int = 20) -> None:
        self.num_workers = num_workers

    def run(self, task: Task, hosts: List[Host]) -> AggregatedResult:
        task_properties = (
            frozenset(task.params.items()),
            task.global_dry_run,
            task.task.__name__,  # Function name in code
            inspect.getmodule(task.task),  # module name and file
        )

        result = AggregatedResult(task.name)
        futures = []
        with ThreadPoolExecutor(self.num_workers) as pool:
            for host in hosts:
                if cached_result := self.CACHE.get((task_properties, host.name), None):
                    result[cached_result.host.name] = cached_result
                    continue
                future = pool.submit(task.copy().start, host)
                futures.append(future)

        for future in futures:
            worker_result = future.result()
            self.CACHE[(task_properties, worker_result.host.name)] = worker_result
            result[worker_result.host.name] = worker_result
        return result
