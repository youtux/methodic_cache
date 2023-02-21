import gc
import sys
import weakref

import pytest

from methodic_cache import cached_method, default_cache_factory

# TODO: Add tests for:
# - using `lock` param
# - test using multiple objects, same method
# - battle-test for memory leaks


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


class TestInvocationVariants:
    def no_parens():
        class Foo:
            @cached_method
            def bar(self, x):
                return [x]

        return Foo

    def with_parens():
        class Foo:
            @cached_method()
            def bar(self, x):
                return [x]

        return Foo

    def with_params():
        class Foo:
            @cached_method(cache_factory=default_cache_factory)
            def bar(self, x):
                return [x]

        return Foo

    @pytest.fixture
    def Foo(self, request):
        return request.param()

    @pytest.mark.parametrize(
        "Foo", [no_parens, with_parens, with_params], indirect=True
    )
    def test_simple(self, Foo):
        foo = Foo()
        res = foo.bar(1)
        assert res == [1]
        bar_cache = Foo.bar.cache(foo)
        assert bar_cache.currsize == 1
        assert foo.bar(1) is res
        assert bar_cache.currsize == 1
        assert foo.bar(2) == [2]
        assert bar_cache.currsize == 2


# TODO: Fix this test
@pytest.mark.xfail(sys.version_info < (3, 10), reason="Failing for some reason")
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


def test_slotted_class_not_supported():
    class Foo:
        __slots__ = ("offset",)

        def __init__(self, offset):
            self.offset = offset

        @cached_method()
        def add(self, x):
            return self.offset + x

    foo = Foo(1)
    with pytest.raises(TypeError, match="need to add.*__weakref__.*__slots__"):
        assert foo.add(1) == 2


def test_slotted_class_supported_if_weakref_slot_present():
    # Ideally we would support slotted classes too
    class Foo:
        __slots__ = ("offset", "__weakref__")

        def __init__(self, offset):
            self.offset = offset

        @cached_method()
        def add(self, x):
            return self.offset + x

    foo = Foo(1)
    assert foo.add(1) == 2
    assert foo.add(2) == 3
    assert Foo.add.cache(foo).currsize == 2


def test_non_hashable_object():
    class Foo:
        __hash__ = None

        @cached_method()
        def lst(self, x):
            return [x]

    foo = Foo()
    with pytest.raises(TypeError, match="unhashable type"):
        {foo}

    res = foo.lst(1)
    assert res == [1]
    assert Foo.lst.cache(foo).currsize == 1
    assert foo.lst(1) is res
