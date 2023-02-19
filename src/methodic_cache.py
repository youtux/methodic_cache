import math
import sys
from collections.abc import MutableMapping
from typing import Callable, Dict, Hashable, Optional, Tuple, TypeVar, Union, overload
from weakref import WeakKeyDictionary

import cachetools

if sys.version_info >= (3, 10):
    from typing import ParamSpec, TypeAlias
else:
    from typing_extensions import ParamSpec, TypeAlias

# TODO: Add support for classes with __slots__


__all__ = ("cached_method",)


P = ParamSpec("P")
T = TypeVar("T")


MethodCache: TypeAlias = MutableMapping

CacheFactory = Callable[[], MethodCache]

ObjectCache: TypeAlias = Dict[Callable[P, T], MethodCache[Tuple[Hashable], T]]

_cache_by_object: WeakKeyDictionary[object, ObjectCache] = WeakKeyDictionary()


def default_cache_factory() -> MethodCache:
    return cachetools.Cache(maxsize=math.inf)


def get_cache(
    obj: object, method: Callable[P, T], cache_factory: Optional[CacheFactory] = None
) -> MutableMapping[Tuple[Hashable], T]:
    try:
        instance_cache = _cache_by_object[obj]
    except KeyError:
        # TODO: Should we use a WeakRefDictionary here too?
        instance_cache = _cache_by_object[obj] = {}

    try:
        method_cache = instance_cache[method]
    except KeyError:
        if cache_factory is None:
            raise TypeError(
                "The cache for the provided object and method was never initialized"
                "and it can't be created, since `cache_factory` param is None"
            )
        method_cache = instance_cache[method] = cache_factory()
    return method_cache


@overload
def cached_method(method: Callable[P, T]) -> Callable[P, T]:
    ...


@overload
def cached_method(
    *, cache_factory: CacheFactory
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    ...


@overload
def cached_method(
    method: Callable[P, T], *, cache_factory: CacheFactory
) -> Callable[P, T]:
    ...


def cached_method(
    method: Optional[Callable[P, T]] = None,
    *,
    cache_factory: CacheFactory = default_cache_factory,
) -> Union[Callable[P, T], Callable[[Callable[P, T]], Callable[P, T]]]:
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
        return get_cache(obj, method, cache_factory)

    # TODO: Add support to override the `lock` and `key` param
    return cachetools.cachedmethod(cache=cache_getter)(method)
