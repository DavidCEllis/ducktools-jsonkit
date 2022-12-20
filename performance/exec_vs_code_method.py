"""
Based on ORJSON's dataclasses performance test.

This is here to show that the 'exec' method of creating a default maker is faster
than using getattr().
"""

import dataclasses

from timeit import timeit

import json
from json_defaults.methods import default_method


ITERATIONS = 100


def old_defaultmaker(method_name):
    """
    Generate a 'default' function that will try to use a named method from objects
    that should be serialized.

    :param method_name: Name of the method to use for serialization
    :return: default function that will make use of that name.
    """
    def default(o):
        try:
            return getattr(o, method_name)()
        except AttributeError:
            raise TypeError(
                f"Object of type {type(o).__name__} is not JSON serializable"
            )
    return default


@dataclasses.dataclass
class Member:
    id: int
    active: bool

    def asdict(self):
        return {'id': self.id, 'active': self.active}


@dataclasses.dataclass
class Object:
    id: int
    name: str
    members: list[Member]

    def asdict(self):
        return {'id': self.id, 'name': self.name, 'members': self.members}


objects_as_dataclass = [
    Object(i, str(i) * 3, [Member(j, True) for j in range(0, 10)])
    for i in range(100000, 102000)
]


new_default = default_method('asdict')
old_default = old_defaultmaker('asdict')

new_data = json.dumps(objects_as_dataclass, default=new_default)
old_data = json.dumps(objects_as_dataclass, default=old_default)

assert new_data == old_data

new_time = timeit(
    lambda: json.dumps(objects_as_dataclass, default=new_default),
    number=ITERATIONS,
)

old_time = timeit(
    lambda: json.dumps(objects_as_dataclass, default=old_default),
    number=ITERATIONS,
)

print("Times")
print(f"old time: {old_time}\nnew time: {new_time}\n")
