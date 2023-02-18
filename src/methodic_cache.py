import math
from collections.abc import MutableMapping
from typing import Any, Callable, Dict, NewType, Optional, TypeVar
from weakref import WeakKeyDictionary

import cachetools

try:
    from typing import TypeAlias  # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import TypeAlias


__all__ = ("cached_method",)


T = TypeVar("T")

# TODO: This should be parametric
Method: TypeAlias = Callable[..., object]

MethodCache: TypeAlias = MutableMapping[Method, object]

ObjectCache = NewType("ObjectCache", Dict[Method, MethodCache])

CacheFactory = Callable[[], MethodCache]


_cache_by_object: WeakKeyDictionary[object, ObjectCache] = WeakKeyDictionary()


def default_cache_factory() -> MethodCache:
    return cachetools.Cache(maxsize=math.inf)


def get_cache(
    obj: object, method: Method, cache_factory: Optional[CacheFactory] = None
) -> MethodCache:
    try:
        instance_cache = _cache_by_object[obj]
    except KeyError:
        # TODO: Should we use a WeakRefDictionary here too?
        instance_cache = _cache_by_object[obj] = ObjectCache({})

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


def cached_method(
    cache_factory: CacheFactory = default_cache_factory,
) -> Callable[[Method], Method]:
    def wrapped_methodcache(method: Method) -> Method:
        def cache_getter(obj: Any) -> MethodCache:
            return get_cache(obj, method, cache_factory)

        cached_method = cachetools.cachedmethod(cache=cache_getter)(method)
        return cached_method

    return wrapped_methodcache
