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
