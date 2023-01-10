import json
from pathlib import Path
from json_defaults import merge_defaults

def test_metadefault():
    def path_default(pth):
        if isinstance(pth, Path):
            return str(pth)
        else:
            raise TypeError()

    def set_default(s):
        if isinstance(s, set):
            return sorted(s)
        else:
            raise TypeError()

    new_default = merge_defaults(path_default, set_default)

    data = {"Path": Path("usr/bin/python"), "versions": {'3.9', '3.10', '3.11'}}
    result = '{"Path": "usr/bin/python", "versions": ["3.10", "3.11", "3.9"]}'

    assert json.dumps(data, default=new_default) == result
