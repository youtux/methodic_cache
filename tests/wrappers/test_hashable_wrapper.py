import pytest

from methodic_cache._wrappers import HashableWrapper


def test_wrapper_is_hashable():
    class Foo:
        __hash__ = None

    foo = Foo()

    with pytest.raises(TypeError, match="unhashable type"):
        {foo}

    wrapped = HashableWrapper(foo)

    assert {wrapped, wrapped} == {wrapped}


def test_hashing_matches():
    class Foo:
        pass

    foo = Foo()

    wrapped = HashableWrapper(foo)
    wrapped2 = HashableWrapper(foo)

    assert wrapped == wrapped2

    assert wrapped in {wrapped2}
    assert wrapped2 in {wrapped}


def test_hashing_does_not_match():
    class Foo:
        pass

    foo1 = Foo()
    foo2 = Foo()

    foo1_w = HashableWrapper(foo1)
    foo2_w = HashableWrapper(foo2)

    assert foo1_w != foo2_w

    assert foo1_w not in {foo2_w}
    assert foo2_w not in {foo1_w}


def test_eq_returns_false_for_other_types():
    class Foo:
        pass

    foo = Foo()

    foo_w = HashableWrapper(foo)

    assert foo_w != foo
    assert foo != foo_w
