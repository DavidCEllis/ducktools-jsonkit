"""
More dataclasses timing

This was used to test the speed of creating the default method.

The new generator seems to be around 4x slower to run the first time, but then
the generated function is faster.
"""

from timeit import timeit
import dataclasses

import json
from json_defaults import dataclass_default, _dc_defaultmaker

ITERATIONS = 50


def old_dc_default(o):
    if dataclasses.is_dataclass(o):
        return {f.name: getattr(o, f.name) for f in dataclasses.fields(o)}


@dataclasses.dataclass
class Object:
    id: int
    name: str
    a: int = 0
    b: int = 2
    c: int = 3
    x: int = 12
    y: int = 13
    z: int = 14


# Time 1 object serialized N times from scratch
total_time = 0
total_cache_time = 0
for i in range(ITERATIONS):
    obj = Object(i, f"{i}")
    total_time += timeit(lambda: json.dumps(obj, default=old_dc_default), number=1)
    total_cache_time += timeit(lambda: json.dumps(obj, default=dataclass_default), number=1)
    _dc_defaultmaker.cache_clear()

print(f"{ITERATIONS} Serializations with cleared Cache: ")
print(f"Basic Method: {total_time}")
print(f"Exec Cached Method: {total_cache_time}")


total_time = timeit(lambda: json.dumps(obj, default=old_dc_default), number=ITERATIONS)
total_cache_time = timeit(lambda: json.dumps(obj, default=dataclass_default), number=ITERATIONS)

print(f"{ITERATIONS} Serializations with cached function: ")
print(f"Basic Method: {total_time}")
print(f"Exec Cached Method: {total_cache_time}")
