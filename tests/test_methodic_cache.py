import gc
import weakref

import pytest

from methodic_cache import cached_method

# TODO: Add tests for:
# - classes with __slots__
# - frozen dataclasses
# - non-hashable object
# - `cache_factory` param
# - using `lock` param
# - test using multiple objects, same method


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


def test_pure_decorator_without_call():
    """Test that we can decorate methods without calling the decorator"""

    class Foo:
        @cached_method
        def lst(self, x):
            return [x]

    foo = Foo()
    res = foo.lst(1)
    assert res == [1]
    assert foo.lst(1) is res
