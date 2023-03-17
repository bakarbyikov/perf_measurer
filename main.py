from functools import wraps
from time import perf_counter, sleep
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

class Timer:
    def __init__(self) -> None:
        self.__elapsed = list()
        self.then = None
    
    @property
    def elapsed(self) -> float:
        return self.__elapsed[-1]
    @property
    def total_time(self) -> float:
        return sum(self.__elapsed)
    @property
    def n_calls(self) -> int:
        return len(self.__elapsed)
    @property
    def average(self) -> float:
        return self.total_time / self.n_calls
    @property
    def min(self) -> float:
        return min(self.__elapsed)
    @property
    def max(self) -> float:
        return max(self.__elapsed)
    
    def start(self) -> None:
        self.then = perf_counter()
    
    def stop(self) -> None:
        elapsed = perf_counter() - self.then
        self.__elapsed.append(elapsed)

class Context_timer(Timer):
    def __enter__(self) -> None:
        self.start()
        return self
    
    def __exit__(self, *_) -> None:
        self.stop()

class Decorator_timer(Timer):
    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def inner(*args: P.args, **kwargs: P.kwargs) -> R:
            self.start()
            res = func(*args, **kwargs)
            self.stop()
            return res
        inner.timer = self
        return inner
    
class Factory:
    def __init__(self) -> None:
        self.instances = dict()

    def __call__(self, something = None) -> Context_timer:
        if something is None:
            return Context_timer()
        if callable(something):
            timer = Decorator_timer()
            name = something.__qualname__
            self.instances[name] = timer
            return timer(something)
        if isinstance(something, str):
            if something in self.instances:
                return self.instances[something]
            timer = Context_timer()
            self.instances[something] = timer
            return timer
        raise NotImplementedError
    
    def print(self) -> None:
        name_width = max(map(len, self.instances.keys()))
        for name, timer in self.instances.items():
            elapsed = timer.elapsed
            calls = timer.n_calls
            avg = timer.average
            print((f"{name:<{name_width}}: "
                   +f"{elapsed=:.2E}, {calls=}, "
                   +f"{avg=:.2E}"))

count_time = Factory()
    
if __name__ == '__main__':
    @count_time
    def test_func(a: int, s: str) -> list:
        sleep(0.01)
        return [a, s, s+str(a)]
    
    for i in range(10):
        test_func(1, '2')
    print(f"function {test_func.timer.elapsed = }")
    
    for i in range(10):
        with count_time('Context test') as timer:
            sleep(0.01)
        print(f"sleeping {timer.elapsed = }")

    count_time.print()
