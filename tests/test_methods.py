import json
from ducktools.jsonkit import method_default


def test_methods_asdict():
    class Example:
        def __init__(self, x, y):
            self.x, self.y = x, y

        def asdict(self):
            return {'x': self.x, 'y': self.y}

    example = Example("hello", "world")
    data = json.dumps(example, default=method_default('asdict'))
    output = '{"x": "hello", "y": "world"}'

    assert data == output
