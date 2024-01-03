from ducktools.jsonkit import JSONRegister

import json
import dataclasses
from pathlib import Path
from decimal import Decimal


def test_json_register():
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

    pypath = f"{str(pth)!r}".replace("'", '"')

    output = (
        '{"id": 42, '
        '"name": "Demonstration Class", '
        f'"location": {pypath}, '
        '"numbers": ['
        '{"cls": "Decimal", "value": "0.001"}, '
        '{"cls": "Decimal", "value": "0.002"}'
        ']}'
    )

    assert json.dumps(demo, default=register.default) == output
