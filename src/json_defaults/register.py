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
        """Decorate a function"""
        def wrapper(func):
            self.register(cls, func)
            return func
        return wrapper

    @property
    def register_method(self):
        """Decorate a class method"""
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
