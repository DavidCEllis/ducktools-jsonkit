# ducktools: jsonkit #

Default functions and default function generators to make JSON serialization
with the python standard library easier.

## Motivation ##

The documentation for the JSON module in the Python standard library (as of 3.11.1)
instructs the user to subclass `JSONEncoder` if you wish to serialize objects
that are not natively serializable. This is unnecessary. The serialization methods
`dump` and `dumps` provide a `default` argument which achieves the same result
without needing to subclass.

This module provides some functions and function generators that can be used as
values for this `default` argument to serialize some standard classes and custom
classes.

Unlike `JSONEncoder` subclasses, `default` functions are also supported as arguments
in some other libraries that implement their own JSON serialization such as
[orjson](https://github.com/ijl/orjson) or
[rapidjson](https://github.com/python-rapidjson/python-rapidjson).

If you're using the `encode` method on a `JSONEncoder` class directly you can provide
the `default` function as an argument to `JSONEncoder` in the same way as to `dumps`.
If `dumps` is being called multiple times with a default, creating a `JSONEncoder` instance
and calling the `encode` method directly will be faster as `dumps` creates a new instance
each time it is called.

## Generated methods for field and dataclass serialization ##

The serializers for dataclasses and fields exist for cases where you need to 
encode a large number of instances of the same dataclass (or other objects 
with the same set of fields).

While calling exec usually takes longer than a single naive serialization, 
the resulting static functions are faster than their dynamic equivalents. 
This is noticeable when serializing a large number of instances of the same class. 
As the results are cached, the cost of `exec` is only paid the first time.

This is actually similar to the method
[cattrs](https://github.com/python-attrs/cattrs)
uses, although that module uses `eval(compile(...))` to provide a 'fake' source
file for inspections. If you're already using
[attrs](https://github.com/python-attrs/attrs)
you should use `cattrs` for serialization.

## Methods ##

The `method_default` function is provided to create a `default` function to pass
to json.dumps if you have classes with a method that is intended to prepare
them for serialization.

Example:

```python
import json
from ducktools.jsonkit import method_default


class Example:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def asdict(self):
        return {'x': self.x, 'y': self.y}


example = Example("hello", "world")

# dumps
data = json.dumps(example, default=method_default('asdict'))

# encoder
encoder = json.JSONEncoder(default=method_default('asdict'))
encoder_data = encoder.encode(example)

print(encoder_data == data)
print(data)
```

Output:
```
True
{"x": "hello", "y": "world"}
```

## Merge defaults ##

The `merge_defaults` function combines multiple `default` functions into one.

```python
import json
from pathlib import Path
from ducktools.jsonkit import merge_defaults


def path_default(pth):
    if isinstance(pth, Path):
        return str(pth)
    else:
        raise TypeError()


def set_default(s):
    if isinstance(s, set):
        return list(s)
    else:
        raise TypeError()


new_default = merge_defaults(path_default, set_default)

data = {"Path": Path("usr/bin/python"), "versions": {'3.9', '3.10', '3.11'}}

print(json.dumps(data, default=new_default))
```

Output:
```
{"Path": "usr/bin/python", "versions": ["3.11", "3.9", "3.10"]}
```

## Register ##

The module provides a `JSONRegister` class that provides methods
to add classes and their serialization methods to the register, these are
then used by providing the `JSONRegister` instance `default` to `json.dumps`.

Example:

```python
from ducktools.jsonkit import JSONRegister

import json
import dataclasses
from pathlib import Path
from decimal import Decimal

register = JSONRegister()


@dataclasses.dataclass
class Demo:
    id: int
    name: str
    location: Path
    numbers: list[Decimal]

    @register.register_method
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'numbers': self.numbers,
        }


register.register(Path, str)


@register.register_function(Decimal)
def unstructure_decimal(val):
    return {'cls': 'Decimal', 'value': str(val)}


numbers = [Decimal(f"{i}") / Decimal('1000') for i in range(1, 3)]
pth = Path("usr/bin/python")

demo = Demo(id=42, name="Demonstration Class", location=pth, numbers=numbers)

print(json.dumps(demo, default=register.default, indent=2))
```

Output:
```
{
  "id": 42,
  "name": "Demonstration Class",
  "location": "usr/bin/python",
  "numbers": [
    {
      "cls": "Decimal",
      "value": "0.001"
    },
    {
      "cls": "Decimal",
      "value": "0.002"
    }
  ]
}
```

## Fields ##

The `field_default` function is intended to be used to handle creating default for
objects where the serialization format is `{name: item.name, ...}`. This is used
for the dataclasses default provided.

For example this could be used to serialize classes based on the field names defined
in `__slots__` (will not work on slots defined by a consumed iterable).

```python
import json
from functools import lru_cache
from ducktools.jsonkit import field_default


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
```

Result:
```
{"x": "Hello", "y": "World"}
```

## Dataclasses ##

Dataclasses itself provides its own `asdict` function, but unfortunately this
includes additional logic for deepcopying objects and performing recursive
serialization.

For the purpose of basic serialization of dataclasses a basic non-recursive
default method will be faster than `asdict`.

Note: The `asdict` method has been improved in Python 3.12+ so the difference
is less significant. 
See [https://github.com/python/cpython/issues/103000](https://github.com/python/cpython/issues/103000).

```python
from dataclasses import is_dataclass, fields
def simple_dc_default(o):
    if is_dataclass(o) and not isinstance(o, type):
        return {f.name: getattr(o, f.name) for f in fields(o)}
    else:
        raise TypeError(
            f'Object of type {type(o).__name__} is not JSON serializable'
        )
```

Using: performance/dataclass_serializers_compared.py

Comparing `asdict`, `simple_dc_default` (simple) and `dataclass_default` (cached).

Python 3.11

| Method           | Time /s | Time /cache |
| ---------------- | ------- | ----------- |
| json asdict      |  4.492  |    3.9 |
| json simple      |  2.400  |    2.1 |
| json cached      |  1.145  |    1.0 |


Python 3.12

| Method           | Time /s | Time /cache |
| ---------------- | ------- | ----------- |
| json asdict      |  1.991  |    2.2 |
| json simple      |  1.910  |    2.1 |
| json cached      |  0.896  |    1.0 |
