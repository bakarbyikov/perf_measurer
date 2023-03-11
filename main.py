from functools import wraps
from time import perf_counter
from typing import Callable, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")

class count_time:
    counted_functions = list()

    @classmethod
    def print(cls) -> None:
        name_width = max(map(lambda x: len(x.__qualname__), cls.counted_functions))
        for f in cls.counted_functions:
            f:Callable
            print((f"{f.__qualname__:<{name_width}}: "
                   +f"elapsed={f.elapsed}, calls={f.calls:.2E}, "
                   +f"avg={f.elapsed/max(1, f.calls):.2E}"))

    @classmethod
    def __call__(cls, func: Callable[P, R]) -> Callable[P, R]:
        cls.counted_functions.append(func)
        
        @wraps(func)
        def inner(*args: P.args, **kwargs: P.kwargs) -> R:
            then = perf_counter()
            res = func(*args, **kwargs)
            func.elapsed += perf_counter() - then
            func.calls += 1

            return res
        
        func.elapsed = 0
        func.calls = 0

        return inner

