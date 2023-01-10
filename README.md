# json_defaults.py #

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

## Exec? ##

Yes this uses exec. 

While calling exec is slow, the resulting static functions are faster than their
dynamic equivalents. This is noticeable when serializing a lot of instances of 
the same class. As the results are cached, the cost of `exec` is only paid the 
first time.

This is actually similar to the method 
[cattrs](https://github.com/python-attrs/cattrs)
uses, although that module uses `eval(compile(...))` to provide a 'fake' source 
file for inspections. If you're already using 
[attrs](https://github.com/python-attrs/attrs)
you should use `cattrs` for serialization.

## Methods ##

The `default_method` function is provided to create a `default` function to pass
to json.dumps if you have classes with a method that is intended to prepare
them for serialization.

Example:

```python
import json
from json_defaults import method_default
class Example:
   def __init__(self, x, y):
       self.x, self.y = x, y
   def asdict(self):
       return {'x': self.x, 'y': self.y}
       
example = Example("hello", "world")
data = json.dumps(example, default=method_default('asdict'))
print(data)
```

Output:
```
{"x": "hello", "y": "world"}
```

## Merge defaults ##

The `mergedefaults` function combines multiple `default` functions into one.

```python
import json
from pathlib import Path
from json_defaults import merge_defaults


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
from json_defaults import JSONRegister

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


numbers = [Decimal(f"{i}")/Decimal('1000') for i in range(1, 3)]
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


## Dataclasses ##

Python's `dataclasses` module does provide an `asdict` function that could
be used to prepare the data for serialization. However this method 
performs all of the recursion itself and calls `deepcopy` on every object
it eventually reaches, which is unnecessary overhead for the use case of 
serialization.

This module provides a serializer for dataclasses
that is around 3x faster than the this method provided by dataclasses if it is 
being used for the purposes of JSON serialization.

This is not as fast as orjson's builtin decoder, but can be useful where orjson
is not available.

Performance:
Using a slightly modified version of `orjson`'s dataclasses test.

* `asdict` - The `asdict` method from the dataclasses module
             this is what orjson used in its original test
* `simple` - `{ field.name: getattr(dc, field.name) for field in fields(dc) }`
* `cached` - The exec/cache based default provided by this module
* `native` - `orjson`'s fast dataclass serializer

| Method           | Time    | Time /orjson native |
| ---------------- | ------- | ------------------- |
| json asdict      |  9.048  |   28.7 |
| json simple      |  4.855  |   15.4 |
| json cached      |  2.632  |    8.3 |
| orjson asdict    |  7.206  |   22.8 |
| orjson simple    |  2.907  |    9.2 |
| orjson cached    |  0.824  |    2.6 |
| orjson native    |  0.315  |    1.0 |
