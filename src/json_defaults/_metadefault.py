def metadefault(defaults):
    def default(o):
        for func in defaults:
            try:
                return func(o)
            except TypeError:
                pass
        else:
            raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")
    return default
