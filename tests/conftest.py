from typing import Iterator

import pytest
from pytest import FixtureRequest


from nornir import InitNornir
from nornir.core import Nornir

from nornir_nuts.runners import CachedThreadedRunner

NORNIR = InitNornir(
    runner={
        "plugin": "cachedThreaded",
        "options": {
            "num_workers": 100,
        },
    },
    inventory={
        "plugin": "SimpleInventory",
        "options": {
            "host_file": "tests/demo_inventory/hosts.yaml",
            "group_file": "tests/demo_inventory/groups.yaml",
        },
    },
)


@pytest.fixture(scope="class")
def nornir() -> Iterator[Nornir]:
    yield NORNIR
    NORNIR.data.reset_failed_hosts()
    if not isinstance(NORNIR.runner, CachedThreadedRunner):
        raise Exception("Nornir is not using the 'CachedThreadedRunner' runner")
    NORNIR.runner.CACHE = {}


@pytest.fixture(params=NORNIR.inventory.hosts.keys())
def nornir_hostname(request: FixtureRequest) -> Iterator[str]:
    yield request.param


# 'host1.cmh','host2.cmh','spine00.cmh','spine01.cmh','leaf00.cmh','leaf01.cmh','host1.bma','host2.bma','spine00.bma','spine01.bma','leaf00.bma','leaf01.bma'
