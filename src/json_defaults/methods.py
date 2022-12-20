from functools import lru_cache


@lru_cache
def default_method(method_name):
    """
    Given a method name, create a `default` function for json.dumps
    that will serialize any objects that have that method.

    :param method_name: name of the method that assists in serializing
    :return: default function to provide to json.dumps
    """
    body = (
        f"def default(o):\n"
        f"    try:\n"
        f"        return o.{method_name}()\n"
        "    except AttributeError:\n"
        "        raise TypeError(f'Object of type {type(o).__name__} is not JSON serializable')\n"
    )

    globs = {}
    exec(body, globs)
    return globs['default']
