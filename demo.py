import logging
import time
from nornir import InitNornir
from nornir.core.task import Task, Result

from random import randrange
from time import sleep


nr = InitNornir(
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


def hello_world(task: Task) -> Result:
    sleep(7)
    return Result(host=task.host, result=f"{task.host.name} says hello world!")


def say(task: Task, text: str) -> Result:
    return Result(host=task.host, result=f"{task.host.name} says {text}")


def count(task: Task, number: int) -> Result:
    count = []
    for i in range(0, number):
        if randrange(10) == 9:
            raise Exception(f"Random exception at number {i}")
        count.append(i)
    return Result(host=task.host, result=f"{count}")


def greet_and_count(task: Task, number: int) -> Result:
    task.run(
        name="Greeting is the polite thing to do",
        task=say,
        text="hi!",
    )

    task.run(
        name="Counting beans", task=count, number=number, severity_level=logging.DEBUG
    )
    task.run(
        name="We should say bye too",
        task=say,
        text="bye!",
    )

    # let's inform if we counted even or odd times
    even_or_odds = "even" if number % 2 == 1 else "odd"
    return Result(host=task.host, result=f"{task.host} counted {even_or_odds} times!")


print("=" * 20, "hello_world 1st run", "=" * 20)
start = time.time()
nr.run(task=hello_world)
print(f"{time.time() - start} seconds")

print("=" * 20, "hello_world 2nd run", "=" * 20)
start = time.time()
nr.run(task=hello_world)
print(f"{time.time() - start} seconds")


print("=" * 20, "count 1st run", "=" * 20)
nr.data.reset_failed_hosts()
result = nr.run(task=count, number=10)
print(f"Hosts {result.failed_hosts.keys()} failed")
for h, r in result.failed_hosts.items():
    print(f"{h}: {r[0].exception}")

print("=" * 20, "count 2nd run", "=" * 20)
nr.data.reset_failed_hosts()
result = nr.run(task=count, number=10)
print(f"Hosts {result.failed_hosts.keys()} failed")
for h, r in result.failed_hosts.items():
    print(f"{h}: {r[0].exception}")

print("=" * 20, "count 3rd run", "=" * 20)
nr.data.reset_failed_hosts()
result = nr.run(task=count, number=10)
print(f"Hosts {result.failed_hosts.keys()} failed")
for h, r in result.failed_hosts.items():
    print(f"{h}: {r[0].exception}")
nr.data.reset_failed_hosts()
