from ducktools.lazyimporter import LazyImporter, MultiFromImport, get_module_funcs

__version__ = "v0.0.3"

__all__ = [
    "merge_defaults",
    "field_default",  # noqa
    "method_default",
    "dataclass_default",  # noqa
    "make_dataclass_default",  # noqa
    "JSONRegister",
]

_laz = LazyImporter(
    [
        MultiFromImport(
            "._caching_tools",
            [
                "field_default",
                "dataclass_default",
                "make_dataclass_default",
            ],
        )
    ],
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
            raise TypeError(
                f"Object of type {type(o).__name__} is not JSON serializable"
            )

    return default


# Serialize using a method name
def method_default(method_name):
    """
    Given a method name, create a `default` function for json.dumps
    that will serialize any objects that have that method.

    :param method_name: name of the method that assists in serializing
    :return: default function to provide to json.dumps
    """

    def default(o):
        try:
            return getattr(o, method_name)()
        except AttributeError:
            raise TypeError(
                f"Object of type {type(o).__name__} is not JSON serializable"
            )

    return default


# Register
class _RegisterDecorator:
    """
    A descriptor used as part of the mechanism to register serializers for classes
    using a decorator.
    """

    def __init__(self, func, registry):
        self.func = func
        self.registry = registry

    def __set_name__(self, owner, name):
        self.registry.register(owner, self.func)
        setattr(owner, name, self.func)


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

        Usage Example: registry.register(Path, str)

        :param cls: Class object to use to identify objects with isinstance
        :param func: Single argument callable that will convert instances of cls
                     into serializable objects
        """
        self.registry.append((cls, func))

    def register_function(self, cls):
        """
        Register a function as a serializer by using a decorator.

        Usage Example:
        @registry.register_function(Decimal)
        def unstructure_decimal(val):
            return {'cls': 'Decimal', 'value': str(val)}

        :param cls: Class the function is being registered for.
        """

        def wrapper(func):
            self.register(cls, func)
            return func

        return wrapper

    def register_method(self, method):
        """
        Register a class method as a serializer by using a decorator.

        Usage Example:
        @dataclasses.dataclass
        class Demo:
            id: int
            name: str
            location: Path
            numbers: list[Decimal]

            @register.register_method
            def to_json(self):
                return {
                    'id': self.id,
                    'name': self.name,
                    'location': self.location,
                    'numbers': self.numbers,
                }

        :param method: The method of a class that converts instances to natively
                       serializable data.
        """

        # In order for this to work the registry needs to know the class that
        # provides the method to be decorated.

        # This isn't available by inspecting the function so a descriptor
        # is created that will be given the class when __set_name__ is called.
        # This descriptor is a non-data descriptor so can be replaced by
        # the original function.

        return _RegisterDecorator(method, self)

    def default(self, o):
        """
        Default function to provide to a json.dumps call as the `default` argument.
        :param o: object to serialize
        :return: serializable data
        """
        for cls, func in self.registry:
            if isinstance(o, cls):
                return func(o)
        raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")
