from json_defaults.slotted import slot_default
import json


class Demo:
    __slots__ = ('id', 'name', 'number')

    def __init__(self, id, name, number):
        self.id, self.name, self.number = id, name, number


data = {f"key {i}": Demo(i, f"key {i}", (i+1)*42) for i in range(2)}

print(json.dumps(data, default=slot_default, indent=2))
