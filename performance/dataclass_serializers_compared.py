"""
Based on ORJSON's dataclasses performance test.
https://github.com/ijl/orjson/blob/master/script/pydataclass

This is here to compare different 'default' methods for serializing dataclasses
"""
from timeit import timeit

import dataclasses

import json
import orjson
# import ujson
# import rapidjson

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

orjson_naive = orjson.dumps(objects_as_dataclass, option=orjson.OPT_PASSTHROUGH_DATACLASS, default=naive_default)
orjson_simple = orjson.dumps(objects_as_dataclass, option=orjson.OPT_PASSTHROUGH_DATACLASS, default=old_dc_default)
orjson_cache = orjson.dumps(objects_as_dataclass, option=orjson.OPT_PASSTHROUGH_DATACLASS, default=dataclass_default)
orjson_native = orjson.dumps(objects_as_dataclass, option=orjson.OPT_SERIALIZE_DATACLASS)

assert orjson_naive == orjson_simple == orjson_cache == orjson_native

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

time_orjson_naive = timeit(
    lambda: orjson.dumps(
        objects_as_dataclass,
        option=orjson.OPT_PASSTHROUGH_DATACLASS,
        default=naive_default
    ).decode("UTF-8"),
    number=ITERATIONS
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
        default=dataclass_default
    ).decode("UTF-8"),
    number=ITERATIONS
)

time_orjson = timeit(
    lambda: orjson.dumps(objects_as_dataclass).decode("UTF-8"),
    number=ITERATIONS
)

# time_rapidjson = timeit(
#     lambda: rapidjson.dumps(objects_as_dataclass, default=dc_default),
#     number=ITERATIONS
# )

# time_ujson = timeit(
#     lambda: ujson.dumps(objects_as_dataclass, default=dc_default),
#     number=ITERATIONS
# )

print("| Method           | Time    | Time /orjson native |")
print("| ---------------- | ------- | ------------------- |")
print(f"| json asdict      |  {time_naive:.3f}  |  {time_naive/time_orjson:5.1f} |")
print(f"| json simple      |  {time_simple:.3f}  |  {time_simple/time_orjson:5.1f} |")
print(f"| json cached      |  {time_cache:.3f}  |  {time_cache/time_orjson:5.1f} |")
print(f"| orjson asdict    |  {time_orjson_naive:.3f}  |  {time_orjson_naive/time_orjson:5.1f} |")
print(f"| orjson simple    |  {time_orjson_simple:.3f}  |  {time_orjson_simple/time_orjson:5.1f} |")
print(f"| orjson cached    |  {time_orjson_cache:.3f}  |  {time_orjson_cache/time_orjson:5.1f} |")
print(f"| orjson native    |  {time_orjson:.3f}  |  {time_orjson/time_orjson:5.1f} |")
# print(f"| rapidjson Cached |  {time_rapidjson:.3f}  |  {time_rapidjson/time_orjson:5.1f} |")
# print(f"| ujson Cached     |  {time_ujson:.3f}  |  {time_ujson/time_orjson:5.1f} |")
