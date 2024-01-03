import json
from dataclasses import dataclass, field, asdict
from ducktools.jsonkit import dataclass_default


def test_dataclass_tojson():
    @dataclass
    class Layer1a:
        x: int
        y: str = "Example1a"

    @dataclass
    class Layer1b:
        v: int
        w: str = "Example1b"

    @dataclass
    class Layer2:
        layers1a: list[Layer1a] = field(default_factory=list)
        layers1b: list[Layer1b] = field(default_factory=list)

    layers_1a = [
        Layer1a(i, f"Example1a_{i}") for i in range(10)
    ]

    layers_1b = [
        Layer1b(i, f"Example1b_{i}") for i in range(15)
    ]

    data = Layer2(layers_1a, layers_1b)

    assert json.dumps(asdict(data)) == json.dumps(data, default=dataclass_default)
