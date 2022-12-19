from timeit import timeit

ITERATIONS = 10_000_000


class X:
    def __init__(self):
        self.x = True


def use_getattr(x):
    return getattr(x, 'x')


def use_dot(x):
    return x.x


x = X()

getattr_time = timeit(lambda: use_getattr(x), number=ITERATIONS)
dot_time = timeit(lambda: use_dot(x), number=ITERATIONS)

print(f"getattr time: {getattr_time}\ndot time: {dot_time}\n")
