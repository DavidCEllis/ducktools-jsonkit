from functools import lru_cache


@lru_cache
def _dc_defaultmaker(cls):
    import dataclasses
    if dataclasses.is_dataclass(cls):
        vals = ", ".join(f"'{item.name}': self.{item.name}"
                         for item in dataclasses.fields(cls))
        out_dict = f"{{{vals}}}"
        funcdef = f"def asdict(self): return {out_dict}"
        globs, locs = {}, {}
        exec(funcdef, globs, locs)
        method = locs['asdict']
        return method
    raise TypeError(f"Object of type {cls.__name__} is not JSON serializable")


def dc_cached_default(o):
    method = _dc_defaultmaker(type(o))
    return method(o)


def dc_default(o):
    import dataclasses
    if dataclasses.is_dataclass(o):
        return {f.name: getattr(o, f.name) for f in dataclasses.fields(o)}
