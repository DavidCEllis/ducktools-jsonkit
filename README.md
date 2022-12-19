# JSON-DEFAULTS.py #

Default functions and default function generators to make `json` serialization
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


## Exec? ##

Yes this uses exec. 

While calling exec is slow, the resulting static functions are faster than their
dynamic equivalents. This is noticeable when serializing a lot of instances of 
the same class. As the results are cached, the cost of `exec` is only paid the 
first time.

## Methods ##

The `make_default` function is provided to create a default function to pass
to json.dumps if you have classes with a method that is intended to prepare
them for serialization.

Example:
```pycon
>>> import json
>>> from json_defaults.methods import make_default
>>> class Example:
...    def __init__(self, x, y):
...        self.x, self.y = x, y
...    def asdict(self):
...        return {'x': self.x, 'y': self.y}
       
>>> example = Example("hello", "world")
>>> default = make_default('asdict')
>>> json.dumps(example, default=default)
'{"x": "hello", "y": "world"}'
```

## Register ##

The register module provides a `JSONRegister` class that provides methods
to add classes and their serialization methods to the register, these are 
then used by providing the `JSONRegister` instance `default` to `json.dumps`.

## Slotted ##

If your classes have the fields you wish to serialize defined in `__slots__` then
`json_defaults.slotted` provides the `slot_default` function that will 
automatically find these fields and construct a dict of the field names
and their values.

## Dataclasses ##

The `json_defaults.dataclasses` module provides a serializer for dataclasses
that is around 3x faster than the asdict method provided by dataclasses if it is 
being used for the purposes of JSON serialization.
