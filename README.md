# Nornir Nuts Plugin

This repository contains Nornir plugins designed for use with Nuts.

# CachedThreaded Runner

The `CachedThreadedRunner` is an extension of the threaded runner from Nornir. Task results are cached in a class variable, and if the cache contains the task result, the cached result is returned. Be aware of the limitations: significant memory consumption is possible, and the results are shared. Therefore, modifying a Result object can lead to side effects.

```bash
pip install nornir-nuts
```

```python
InitNornir(
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
```