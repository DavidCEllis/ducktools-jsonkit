"""
Based on ORJSON's dataclasses performance test.

This is here to compare different 'default' methods for serializing dataclasses
"""
from timeit import timeit

import dataclasses

import json
import orjson
from json_defaults.dataclasses import dc_default


ITERATIONS = 500


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
result_cache = json.dumps(objects_as_dataclass, default=dc_default)

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
    lambda: json.dumps(objects_as_dataclass, default=dc_default),
    number=ITERATIONS,
)

time_orjson_simple = timeit(
    lambda: orjson.dumps(
        objects_as_dataclass,
        option=orjson.OPT_PASSTHROUGH_DATACLASS,
        default=old_dc_default
    ).decode("UTF-8"),
    number=ITERATIONS
)

time_orjson_cache = timeit(
    lambda: orjson.dumps(
        objects_as_dataclass,
        option=orjson.OPT_PASSTHROUGH_DATACLASS,
        default=dc_default
    ).decode("UTF-8"),
    number=ITERATIONS
)

time_orjson = timeit(
    lambda: orjson.dumps(objects_as_dataclass).decode("UTF-8"),
    number=ITERATIONS
)

print("Times:")
print(f"Naive Default:  {time_naive:.3f}  |  {time_naive/time_orjson:4.1f}")
print(f"Simple Default: {time_simple:.3f}  |  {time_simple/time_orjson:4.1f}")
print(f"Cached Default: {time_cache:.3f}  |  {time_cache/time_orjson:4.1f}")
print(f"ORJSON Simple:  {time_orjson_simple:.3f}  |  {time_orjson_simple/time_orjson:4.1f}")
print(f"ORJSON Cached:  {time_orjson_cache:.3f}  |  {time_orjson_cache/time_orjson:4.1f}")
print(f"ORJSON:         {time_orjson:.3f}  |  {time_orjson/time_orjson:4.1f}")
