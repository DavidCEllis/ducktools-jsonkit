from json_defaults.register import JSONRegister

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
