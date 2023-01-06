import json
from json_defaults.methods import default_method


def test_methods_asdict():
    class Example:
        def __init__(self, x, y):
            self.x, self.y = x, y

        def asdict(self):
            return {'x': self.x, 'y': self.y}


    example = Example("hello", "world")
    data = json.dumps(example, default=default_method('asdict'))
    output = '{"x": "hello", "y": "world"}'

    assert data == output
