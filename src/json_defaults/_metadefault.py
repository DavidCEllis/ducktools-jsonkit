def metadefault(*defaults):
    """
    Combine multiple default functions into one.

    Default functions are expected to return serializable objects or raise a TypeError

    :param defaults: 'default' functions for json.dumps
    :return: merged default function
    """
    def default(o):
        for func in defaults:
            try:
                return func(o)
            except TypeError:
                pass
        else:
            raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")
    return default
