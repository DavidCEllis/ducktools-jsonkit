import dataclasses

from timeit import timeit

import json
from json_defaults.methods import defaultmaker


ITERATIONS = 500


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
        except (AttributeError, TypeError):
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


new_default = defaultmaker('asdict')
old_default = old_defaultmaker('asdict')

assert json.dumps(objects_as_dataclass, default=new_default) == json.dumps(objects_as_dataclass, default=old_default)

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
