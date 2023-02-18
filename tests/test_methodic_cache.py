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
