# methodic_cache

[![codecov](https://codecov.io/gh/youtux/methodic_cache/branch/main/graph/badge.svg?token=7LSah9W8zt)](https://codecov.io/gh/youtux/methodic_cache)

`functools.cache()` for methods, done correctly.


# Features
* Simple to use
* Extendable with [custom cache backends](#custom-cache-backends) (e.g. LRUCache, LFUCache, etc.)
* Works with non-hashable objects
* Works with [frozen/slotted classes](#using-classes-with-__slots__)
* Tested for memory leaks

# Installation
```bash
pip install methodic_cache
```

# Usage
```python
from methodic_cache import cached_method


class MyClass:
    @cached_method
    def my_method(self, arg1, arg2):
        return arg1 + arg2


my_obj = MyClass()
my_obj.my_method(1, 2)  # returns 3
my_obj.my_method(1, 2)  # returns 3 from the cache
```


## Using classes with `__slots__`
Classes that define `__slots__` need to have a `__weakref__` slot to be able to be weakly referenced:

```python
from methodic_cache import cached_method


class MyClass:
    __slots__ = ("my_attr", "__weakref__")  # <-- __weakref__ is required

    def __init__(self, my_attr):
        self.my_attr = my_attr

    @cached_method
    def my_method(self, arg1, arg2):
        print(f"Computing {self.my_attr} + {arg1} + {arg2}...")
        return self.my_attr + arg1 + arg2

my_obj = MyClass(1)
my_obj.my_method(2, 3)
# prints "Computing 1 + 2 + 3..."
# returns 6
my_obj.my_method(2, 3)
# returns 6
```


## Custom cache backends
You can use any cache backend that implements the `MutableMapping` interface (e.g. `dict`, `lru_cache`, `functools.lru_cache`, etc.).
The default cache backend is `cachetools.Cache(maxsize=math.inf)`, which will keep the cache bounded to the lifetime of the `self` object.

You can use a different cache backend by passing it as the `cache_factory` argument to `cached_method`:

```python
from methodic_cache import cached_method
from cachetools import LRUCache


class MyClass:
    @cached_method(cache_factory=lambda: LRUCache(maxsize=1))
    def my_method(self, arg1, arg2):
        print(f"Computing {arg1} + {arg2}...")
        return arg1 + arg2


my_obj = MyClass()
my_obj.my_method(1, 1)
# prints Computing 1 + 1...
# returns 2
my_obj.my_method(1, 1)
# returns 2
my_obj.my_method(2, 2)
# prints Computing 2 + 2...
# returns 4
my_obj.my_method(1, 1)  # <-- this will be recomputed because the cache is full
# prints Computing 1 + 1...
# returns 2
```
