from typing import Tuple
from abc import ABC
from random import randrange
import pytest
import time

from nornir.core import Nornir
from nornir.core.task import Task, Result, AggregatedResult

from nornir_nuts.runners import CachedThreadedRunner


class BaseCacheTest(ABC):
    CACHE_LEN = 0

    def test_cache_size(
        self, nornir: Nornir, results: Tuple[AggregatedResult, AggregatedResult]
    ) -> None:
        assert isinstance(nornir.runner, CachedThreadedRunner)
        assert len(nornir.runner.CACHE) == self.CACHE_LEN


class TestRandomNumber(BaseCacheTest):
    CACHE_LEN = 12

    @pytest.fixture(scope="class")
    def results(self, nornir: Nornir) -> Tuple[AggregatedResult, AggregatedResult]:
        def random_number(task: Task) -> Result:
            return Result(host=task.host, result=randrange(0, 1000))

        result1 = nornir.run(task=random_number)
        result2 = nornir.run(task=random_number)
        return result1, result2

    def test_result(
        self,
        nornir: Nornir,
        nornir_hostname: str,
        results: Tuple[AggregatedResult, AggregatedResult],
    ) -> None:
        result1 = results[0]
        result2 = results[1]

        assert hasattr(nornir.runner, "CACHE")
        assert result1[nornir_hostname][0].result == result2[nornir_hostname][0].result


class TestSubtaskDifferentMethods(BaseCacheTest):
    CACHE_LEN = 24

    @pytest.fixture(scope="class")
    def results(self, nornir: Nornir) -> Tuple[AggregatedResult, AggregatedResult]:
        def sub1(task: Task) -> Result:
            def my_task(task: Task) -> Result:
                return Result(host=task.host, result="sub1")

            task.run(my_task)
            return Result(host=task.host)

        def sub2(task: Task) -> Result:
            def my_task(task: Task) -> Result:
                return Result(host=task.host, result="sub2")

            task.run(my_task)
            return Result(host=task.host)

        result1 = nornir.run(task=sub1)
        result2 = nornir.run(task=sub2)
        return result1, result2

    def test_result(
        self,
        nornir: Nornir,
        nornir_hostname: str,
        results: Tuple[AggregatedResult, AggregatedResult],
    ) -> None:
        result1 = results[0]
        result2 = results[1]

        assert hasattr(nornir.runner, "CACHE")
        assert result1[nornir_hostname][1].result == "sub1"
        assert result2[nornir_hostname][1].result == "sub2"
