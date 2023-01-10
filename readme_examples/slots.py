import json
from functools import lru_cache
from json_defaults import field_default


@lru_cache
def slot_defaultmaker(cls):
    try:
        slots = cls.__slots__
    except AttributeError:
        raise TypeError(f'Object of type {cls.__name__} is not JSON serializable')
    slot_tuple = tuple(slots)
    return field_default(slot_tuple)


def slot_default(o):
    func = slot_defaultmaker(type(o))
    return func(o)


class SlotExample:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x, self.y = x, y


example = SlotExample("Hello", "World")

data = json.dumps(example, default=slot_default)
print(data)
