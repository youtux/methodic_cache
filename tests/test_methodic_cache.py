import gc
import sys
import weakref

import pytest

from methodic_cache import cached_method, simple_cache_factory

# TODO: Add tests for:
# - using `lock` param
# - battle-test for memory leaks


def test_method_no_params():
    class Foo:
        @cached_method()
        def bar(self):
            return [self]

    foo = Foo()
    res = foo.bar()
    assert foo.bar() is res
    assert Foo.bar.cache(foo).currsize == 1


def test_cache_on_params():
    """Test that passing different params to the same method doesn't use the cache"""

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


def test_cache_empty_if_no_calls():
    class Foo:
        @cached_method()
        def bar(self, x):
            return x

    foo = Foo()
    assert Foo.bar.cache(foo).currsize == 0


def test_cache_persists_as_long_as_object_does():
    class Foo:
        @cached_method()
        def bar(self, x):
            return x

    foo = Foo()
    foo_bar_cache = Foo.bar.cache(foo)
    foo.bar(1)
    assert Foo.bar.cache(foo) is foo_bar_cache
    assert foo_bar_cache.currsize == 1


def test_multiple_objects_same_method():
    """Test that different objects don't share the same cache"""

    class Foo:
        @cached_method()
        def bar(self, x):
            return [x]

    foo1 = Foo()

    foo2 = Foo()
    foo1_1 = foo1.bar(1)

    foo2_1 = foo2.bar(1)
    assert foo1_1 is not foo2_1


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
            @cached_method(cache_factory=simple_cache_factory)
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


def test_slotted_class_without_weakref_slot_are_not_supported():
    """Test that slotted classes are not supported if they don't have a
    __weakref__ slot"""

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
    """Test that slotted classes are supported if they have a __weakref__ slot"""

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
    """Test that non-hashable objects work normally"""

    class Foo:
        __hash__ = None

        @cached_method()
        def lst(self, x):
            return [x]

    foo = Foo()
    with pytest.raises(TypeError, match="unhashable type"):
        # Make sure that foo is indeed not hashable
        {foo}

    res = foo.lst(1)
    assert res == [1]
    assert Foo.lst.cache(foo).currsize == 1
    assert foo.lst(1) is res
