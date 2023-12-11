from ducktools.lazyimporter import LazyImporter, MultiFromImport, get_module_funcs

__version__ = "v0.0.3"

__all__ = [
    "merge_defaults",
    "field_default",  # noqa
    "method_default",  # noqa
    "dataclass_default", # noqa
    "make_dataclass_default", # noqa
    "JSONRegister",
]


_laz = LazyImporter(
    [MultiFromImport(
        "._caching_tools",
        ["field_default", "method_default", "dataclass_default", "make_dataclass_default"]
    )],
    globs=globals(),
)

__getattr__, __dir__ = get_module_funcs(_laz, __name__)


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
