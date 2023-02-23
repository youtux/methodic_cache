import gc
import weakref

from methodic_cache import cached_method, simple_cache_factory


def test_memory_leaks() -> None:
    class Foo:
        @cached_method
        def bar(self, x):
            return [x]

    foo = Foo()
    foo_weak = weakref.ref(foo)
    res = foo.bar(1)
    del foo

    gc.collect()
    assert foo_weak() is None


def __main__():
    raise SystemExit(0)


if __name__ == "__main__":
    __main__()
