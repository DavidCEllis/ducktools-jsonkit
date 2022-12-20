import json
from functools import partial, lru_cache
from timeit import timeit

import attrs
from attrs import define
import cattrs.preconf.json


ITERATIONS = 20


@define
class Member:
    id: int
    active: bool


@define
class Object:
    id: int
    name: str
    members: list[Member]


objects_as_dataclass = [
    Object(i, str(i) * 3, [Member(j, True) for j in range(0, 10)])
    for i in range(100000, 102000)
]


def attrs_unstructure(o):
    return json.dumps([attrs.asdict(item) for item in o])


def attrs_nonrecursive_default(o):
    asdict_norecurse = partial(attrs.asdict, recurse=False)
    return json.dumps(o, default=asdict_norecurse)


converter = cattrs.preconf.json.make_converter()


def cattrs_serialize(o):
    return converter.dumps(o)


@lru_cache
def field_names(attrs_cls):
    return [f.name for f in attrs.fields(attrs_cls)]


def basic_asdict(o):
    flds = field_names(type(o))
    return {f: getattr(o, f) for f in flds}


@lru_cache
def attrs_default_maker(attrs_cls, exclude_fields=None):
    try:
        if exclude_fields:
            vals = ", ".join(f"'{item.name}': self.{item.name}"
                             for item in attrs.fields(attrs_cls)
                             if item.name not in exclude_fields)
        else:
            vals = ", ".join(f"'{item.name}': self.{item.name}"
                             for item in attrs.fields(attrs_cls))
    except attrs.exceptions.NotAnAttrsClassError:
        raise TypeError(f"Object of type {attrs_cls.__name__} is not JSON serializable")

    out_dict = f"{{{vals}}}"
    funcdef = f"def asdict(self): return {out_dict}"
    globs, locs = {}, {}
    exec(funcdef, globs, locs)
    method = locs['asdict']
    return method


def basic_serialize(o):
    return json.dumps(o, default=basic_asdict)


def exec_default(o):
    return attrs_default_maker(type(o))(o)


def exec_serialize(o):
    return json.dumps(o, default=exec_default)


attrs_basic = attrs_unstructure(objects_as_dataclass)
attrs_norecurse = attrs_nonrecursive_default(objects_as_dataclass)
cattrs_result = cattrs_serialize(objects_as_dataclass)
basic_result = basic_serialize(objects_as_dataclass)
exec_result = exec_serialize(objects_as_dataclass)

assert attrs_basic == attrs_norecurse == cattrs_result == basic_result == exec_result

recurse_time = timeit(
    lambda: attrs_unstructure(objects_as_dataclass),
    number=ITERATIONS
)

norecurse_time = timeit(
    lambda: attrs_nonrecursive_default(objects_as_dataclass),
    number=ITERATIONS
)

cattrs_time = timeit(
    lambda: cattrs_serialize(objects_as_dataclass),
    number=ITERATIONS
)

basic_time = timeit(
    lambda: basic_serialize(objects_as_dataclass),
    number=ITERATIONS
)

exec_time = timeit(
    lambda: exec_serialize(objects_as_dataclass),
    number=ITERATIONS
)

print(recurse_time, norecurse_time, cattrs_time, basic_time, exec_time)
