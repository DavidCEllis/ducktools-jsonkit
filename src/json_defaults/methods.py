def make_default(method_name):
    try_statement = (
        "    try: \n"
        f"        return o.{method_name}()\n"
    )
    except_statement = (
        "    except AttributeError: \n"
        "        raise TypeError(f'Object of type {type(o).__name__} is not JSON serializable')\n"
    )
    def_statement = "def default(o): \n"
    body = f"{def_statement}{try_statement}{except_statement}\n"

    globs, locs = {}, {}
    exec(body, globs, locs)
    return locs['default']
