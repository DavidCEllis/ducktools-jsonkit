"""
Based on ORJSON's dataclasses performance test.
https://github.com/ijl/orjson/blob/master/script/pydataclass

This is here to compare different 'default' methods for serializing dataclasses
"""
from timeit import timeit

import dataclasses

import json

from json_defaults.dataclasses import dataclass_default


ITERATIONS = 100


# NAIVE SERIALIZER #

def naive_default(o):
    return dataclasses.asdict(o)


def old_dc_default(o):
    if dataclasses.is_dataclass(o):
        return {f.name: getattr(o, f.name) for f in dataclasses.fields(o)}


# DATA INPUT #

@dataclasses.dataclass
class Member:
    id: int
    active: bool


@dataclasses.dataclass
class Object:
    id: int
    name: str
    members: list[Member]


objects_as_dataclass = [
    Object(i, str(i) * 3, [Member(j, True) for j in range(0, 10)])
    for i in range(100000, 102000)
]

result_naive = json.dumps(objects_as_dataclass, default=naive_default)
result_simple = json.dumps(objects_as_dataclass, default=old_dc_default)
result_cache = json.dumps(objects_as_dataclass, default=dataclass_default)

# Check they all output the same thing
assert result_naive == result_simple == result_cache

time_naive = timeit(
    lambda: json.dumps(objects_as_dataclass, default=naive_default),
    number=ITERATIONS,
)

time_simple = timeit(
    lambda: json.dumps(objects_as_dataclass, default=old_dc_default),
    number=ITERATIONS,
)

time_cache = timeit(
    lambda: json.dumps(objects_as_dataclass, default=dataclass_default),
    number=ITERATIONS,
)


print("| Method           | Time /s | Time /cache |")
print("| ---------------- | ------- | ----------- |")
print(f"| json asdict      |  {time_naive:.3f}  |  {time_naive/time_cache:5.1f} |")
print(f"| json simple      |  {time_simple:.3f}  |  {time_simple/time_cache:5.1f} |")
print(f"| json cached      |  {time_cache:.3f}  |  {time_cache/time_cache:5.1f} |")
