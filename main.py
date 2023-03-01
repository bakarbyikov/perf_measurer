from time import perf_counter
from typing import Callable


class count_time:
    counted_functions = list()

    @classmethod
    def print(cls) -> None:
        for f in cls.counted_functions:
            print((f"func={f.__module__}.{f.__name__}: "
                   +f"elapsed={f.elapsed}, calls={f.calls}, "
                   +f"avg={f.elapsed/max(1, f.calls)}"))

    @classmethod
    def __call__(cls, func: Callable) -> Callable:
        cls.counted_functions.append(func)
        
        def inner(*args, **kwds):
            then = perf_counter()
            res = func(*args, **kwds)
            func.elapsed += perf_counter() - then
            func.calls += 1

            return res
        
        func.elapsed = 0
        func.calls = 0

        return inner