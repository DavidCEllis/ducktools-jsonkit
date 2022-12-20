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

print("Accessing a variable 10,000,000 times")
print("| Method | Time /s |")
print("| ------ | ------- |")
print(f"| getattr | {getattr_time:.3f}s |\n| dot | {dot_time:.3f}s |\n")
