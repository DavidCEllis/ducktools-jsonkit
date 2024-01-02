from ducktools.lazyimporter import LazyImporter, ModuleImport
from functools import lru_cache


_laz = LazyImporter([ModuleImport("dataclasses")])


# Serialize by field names
@lru_cache
def field_default(fieldnames):
    """
    Create a function that will take an object and return a
    {fieldname: obj.fieldname, ...} dictionary.

    (Fieldnames must be hashable so can not be a list.)

    :param fieldnames: tuple of fieldnames
    :return: dict conversion function
    """
    vals = ", ".join(f"'{fieldname}': o.{fieldname}" for fieldname in fieldnames)
    out_dict = f"{{{vals}}}"
    funcdef = (
        f"def default(o):\n"
        f"    try:\n"
        f"        return {out_dict}\n"
        f"    except AttributeError:\n"
        f"        raise TypeError(\n"
        f"            f'Object of type {{type(o).__name__}} is not JSON serializable'\n"
        f"        )\n"
    )
    globs = {}
    exec(funcdef, globs)
    method = globs["default"]
    return method


# Serialize Dataclasses
@lru_cache
def _dc_defaultmaker(cls, exclude_fields=()):
    if not _laz.dataclasses.is_dataclass(cls):
        raise TypeError(f"Object of type {cls.__name__} is not JSON serializable")

    field_names = tuple(
        item.name
        for item in _laz.dataclasses.fields(cls)
        if item.name not in exclude_fields
    )

    method = field_default(field_names)  # type: ignore
    return method


def make_dataclass_default(exclude_fields):
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
