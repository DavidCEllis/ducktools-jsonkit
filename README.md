# JSON-DEFAULTS.py #

Default functions and assistants to make serialization of python object to JSON
easier.

## Methods ##

The `methods` module provides a `default` function generator for any given method name.

Example:
```pycon
>>> from json_defaults.methods import default_maker
>>> class Example:
...    def __init__(self, x, y):
...        self.x, self.y = x, y
...    def asdict(self):
...        return {'x': self.x, 'y': self.y}
       
>>>  
```

## Register ##

