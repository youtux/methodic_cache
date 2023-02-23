from __future__ import annotations

import math
import sys
from typing import Callable, Dict, Hashable, MutableMapping, Tuple, TypeVar, overload
from weakref import WeakKeyDictionary

import cachetools

from ._wrappers import HashableWrapper

if sys.version_info >= (3, 10):
    from typing import ParamSpec, TypeAlias
else:
    from typing_extensions import ParamSpec, TypeAlias


P = ParamSpec("P")
T = TypeVar("T")


MethodCache: TypeAlias = MutableMapping

CacheFactory = Callable[[], MethodCache]

ObjectCache: TypeAlias = Dict[Callable[P, T], MethodCache[Tuple[Hashable], T]]

_cache_by_object: WeakKeyDictionary[object, ObjectCache] = WeakKeyDictionary()


def simple_cache_factory() -> MethodCache:
    return cachetools.Cache(maxsize=math.inf)


def ensure_cache(
    obj: object, method: Callable[P, T], cache_factory: CacheFactory
) -> MutableMapping[tuple[Hashable], T]:
    w = HashableWrapper(obj)
    try:
        instance_cache = _cache_by_object[w]
    except KeyError:
        # TODO: Should we use a WeakRefDictionary here too?
        instance_cache = _cache_by_object[w] = {}

    try:
        method_cache = instance_cache[method]
    except KeyError:
        method_cache = instance_cache[method] = cache_factory()
    return method_cache


@overload
def cached_method(
    *, cache_factory: CacheFactory = ...
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    ...  # pragma: no cover


@overload
def cached_method(
    method: Callable[P, T], *, cache_factory: CacheFactory = ...
) -> Callable[P, T]:
    ...  # pragma: no cover


def cached_method(
    method: Callable[P, T] | None = None,
    *,
    cache_factory: CacheFactory = simple_cache_factory,
) -> Callable[P, T] | Callable[[Callable[P, T]], Callable[P, T]]:
    if method is None:

        def wrapper(method: Callable[P, T]) -> Callable[P, T]:
            return cached_method(method, cache_factory=cache_factory)

        return wrapper

    def cache_getter(obj: object) -> MethodCache:
        slots = getattr(type(obj), "__slots__", None)
        if slots is not None and "__weakref__" not in slots:
            raise TypeError(
                "In order for `cached_method` to support classes with __slots__, "
                'you need to add the "__weakref__" attribute to the __slots__'
            )

        assert method is not None  # for mypy
        return ensure_cache(obj, method, cache_factory)

    # TODO: Add support to override the `lock` and `key` param
    return cachetools.cachedmethod(cache=cache_getter)(method)
