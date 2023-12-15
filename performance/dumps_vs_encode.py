"""
Based on ORJSON's dataclasses performance test.
https://github.com/ijl/orjson/blob/master/script/pydataclass

This is here to compare using dumps vs creating a JSONEncoder and just timing the
encode method.
"""
from timeit import timeit

import dataclasses

import json

from ducktools.jsonkit import dataclass_default


ITERATIONS = 100


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

dataclass_encoder = json.JSONEncoder(default=dataclass_default)

# Create the cache
dataclass_encoder.encode(objects_as_dataclass)


time_dumps = timeit(
    lambda: json.dumps(objects_as_dataclass, default=dataclass_default),
    number=ITERATIONS,
)

time_encoder = timeit(
    lambda: dataclass_encoder.encode(objects_as_dataclass),
    number=ITERATIONS,
)

print("| Method           | Time /s | Time /cache |")
print("| ---------------- | ------- | ----------- |")
print(f"| json encoder     |  {time_encoder:.3f}  |  {time_encoder/time_dumps:5.1f} |")
print(f"| json dumps       |  {time_dumps:.3f}  |  {time_dumps/time_dumps:5.1f} |")
