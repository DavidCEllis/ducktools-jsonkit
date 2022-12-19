from functools import lru_cache

import dataclasses


@lru_cache
def _dc_defaultmaker(cls):
    if not dataclasses.is_dataclass(cls):
        raise TypeError(f"Object of type {cls.__name__} is not JSON serializable")

    vals = ", ".join(f"'{item.name}': self.{item.name}"
                     for item in dataclasses.fields(cls))
    out_dict = f"{{{vals}}}"
    funcdef = f"def asdict(self): return {out_dict}"
    globs, locs = {}, {}
    exec(funcdef, globs, locs)
    method = locs['asdict']
    return method


def dc_default(o):
    method = _dc_defaultmaker(type(o))
    return method(o)
