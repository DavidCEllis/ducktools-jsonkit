from functools import lru_cache

import dataclasses


@lru_cache
def _dc_defaultmaker(cls, exclude_fields=None):
    if not dataclasses.is_dataclass(cls):
        raise TypeError(f"Object of type {cls.__name__} is not JSON serializable")
    if exclude_fields:
        vals = ", ".join(f"'{item.name}': self.{item.name}"
                         for item in dataclasses.fields(cls)
                         if item.name not in exclude_fields)
    else:
        vals = ", ".join(f"'{item.name}': self.{item.name}"
                         for item in dataclasses.fields(cls))
    out_dict = f"{{{vals}}}"
    funcdef = f"def asdict(self): return {out_dict}"
    globs = {}
    exec(funcdef, globs)
    method = globs['asdict']
    return method


def make_dataclass_default(exclude_fields: tuple[str]):
    """
    Make a 'default' function to serialize dataclasses that will
    exclude specific named fields.

    :param exclude_fields: tuple of field names to exclude from serialization.
    :return: 'default' function to use with json.dumps
    """
    def dataclass_excludes_default(o):
        method = _dc_defaultmaker(type(o), exclude_fields)
        return method(o)
    return dataclass_excludes_default


def dataclass_default(o):
    """
    Function to provide to `json.dumps` to allow basic serialization
    of dataclass objects.
    """
    method = _dc_defaultmaker(type(o))
    return method(o)
