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
    globs, locs = {}, {}
    exec(funcdef, globs, locs)
    method = locs['asdict']
    return method


def make_default_excludes(exclude_fields: tuple[str]):
    def dc_excludes_default(o):
        method = _dc_defaultmaker(type(o), exclude_fields)
        return method(o)
    return dc_excludes_default


def dc_default(o):
    method = _dc_defaultmaker(type(o))
    return method(o)
