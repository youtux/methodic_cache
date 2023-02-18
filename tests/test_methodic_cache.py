import gc
import weakref

from methodic_cache import cached_method


def test_simple():
    class Foo:
        @cached_method()
        def bar(self, x):
            return x

    foo = Foo()
    assert foo.bar(1) == 1
    bar_cache = Foo.bar.cache(foo)
    assert bar_cache.currsize == 1
    assert foo.bar(1) == 1
    assert bar_cache.currsize == 1
    assert foo.bar(2) == 2
    assert bar_cache.currsize == 2


def test_no_leaks():
    class Foo:
        @cached_method()
        def bar(self, x):
            return x | {"foo"}

    foo = Foo()
    param = frozenset()

    res = foo.bar(param)
    assert foo.bar(param) is res

    foo_ref = weakref.ref(foo)
    param_ref = weakref.ref(param)
    res_ref = weakref.ref(res)

    del foo
    del param
    del res

    gc.collect()

    assert foo_ref() is None
    assert param_ref() is None
    assert res_ref() is None
