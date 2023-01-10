from functools import lru_cache

__version__ = "v0.0.2"

__all__ = [
    "merge_defaults",
    "field_default",
    "method_default",
    "dataclass_default",
    "make_dataclass_default",
    "JSONRegister",
]


# Merge multiple defaults
def merge_defaults(*defaults):
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


# Serialize by field names
@lru_cache
def field_default(fieldnames: tuple[str]):
    """
    Create a function that will take an object and return a {fieldname: obj.fieldname, ...}
    dictionary.

    (Fieldnames must be hashable so can not be a list.)

    :param fieldnames: tuple of fieldnames
    :return: dict conversion function
    """
    vals = ", ".join(f"'{fieldname}': o.{fieldname}"
                     for fieldname in fieldnames)
    out_dict = f"{{{vals}}}"
    funcdef = (
        u"def default(o):\n"
        u"    try:\n"
        f"        return {out_dict}\n"
        u"    except AttributeError:\n"
        u"        raise TypeError(f'Object of type {type(o).__name__} is not JSON serializable')\n"
    )
    globs = {}
    exec(funcdef, globs)
    method = globs['default']
    return method


# Serialize using a method name
@lru_cache
def method_default(method_name):
    """
    Given a method name, create a `default` function for json.dumps
    that will serialize any objects that have that method.

    :param method_name: name of the method that assists in serializing
    :return: default function to provide to json.dumps
    """
    body = (
        u"def default(o):\n"
        u"    try:\n"
        f"        return o.{method_name}()\n"
        u"    except AttributeError:\n"
        u"        raise TypeError(f'Object of type {type(o).__name__} is not JSON serializable')\n"
    )

    globs = {}
    exec(body, globs)
    return globs['default']


# Serialize Dataclasses
@lru_cache
def _dc_defaultmaker(cls, exclude_fields: tuple[str] = ()):
    import dataclasses
    if not dataclasses.is_dataclass(cls):
        raise TypeError(f"Object of type {cls.__name__} is not JSON serializable")

    field_names = tuple(
        item.name
        for item in dataclasses.fields(cls)
        if item.name not in exclude_fields
    )

    method = field_default(field_names)
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


# Register
class JSONRegister:
    """
    Register methods for serializing classes, provides a 'default' method
    to give to `dumps` style functions.

    Provides a method to add a serializer for any class and two decorators
    to decorate functions and class methods to register them as serializers.
    """
    def __init__(self):
        self.registry = []

    def register(self, cls, func):
        """
        Register a function that will convert a class instance into something
        that is serializable by the json.dumps function.

        :param cls: Class object
        :param func: Single argument callable that will convert instances of cls
                     into serializable objects
        """
        self.registry.append((cls, func))

    def register_function(self, cls):
        """Register a function as a serializer by using a decorator"""
        def wrapper(func):
            self.register(cls, func)
            return func
        return wrapper

    @property
    def register_method(self):
        """Register a class method as a serializer by using a decorator"""

        # Pycharm will complain about using 'inst' and not 'self'
        # 'self' would not work because it is in the outer scope.
        # noinspection PyMethodParameters
        class RegisterDecorator:
            def __init__(inst, func):
                inst.func = func

            def __set_name__(inst, owner, name):
                self.register(owner, inst.func)
                setattr(owner, name, inst.func)

        return RegisterDecorator

    def default(self, o):
        """
        Default function to provide to a json.dumps call as the `default` argument.
        :param o: object to serialize
        :return: serializable data
        """
        for cls, func in self.registry:
            if isinstance(o, cls):
                return func(o)
        raise TypeError(
            f"Object of type {o.__class__.__name__} is not JSON serializable"
        )
