from functools import lru_cache


@lru_cache
def _slot_serializer(slot_field):
    if isinstance(slot_field, str):
        slot_field = [slot_field]

    names = ", ".join(f"'{field}': o.{field}" for field in slot_field)
    func = f"def new_default(o): return {{{names}}}"

    globs = {}
    exec(func, globs)
    return globs["new_default"]


def slot_default(o):
    """
    JSON default serializer for classes with declared __slots__

    :param o: instance of slotted class
    :return: dict of {slot_name: value, ...}
    """
    try:
        slots = o.__slots__
    except AttributeError:
        # No __slots__
        raise TypeError(f'Object of type {type(o).__name__} is not JSON serializable')

    try:
        default = _slot_serializer(slots)
    except TypeError:
        # unhashable slots - attempt to convert to tuple
        slots = tuple(slots)
        default = _slot_serializer(slots)

    return default(o)
