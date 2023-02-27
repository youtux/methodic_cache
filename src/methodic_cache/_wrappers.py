from __future__ import annotations

from collections.abc import Hashable
from weakref import WeakValueDictionary

from methodic_cache._exceptions import ObjectDoesNotSupportWeakRef


class HashableWrapper(Hashable):
    """Wrapper for objects that are not hashable.

    It will stay alive as long as the object is alive.
    """

    __slots__ = ("key", "obj", "__weakref__")

    def __init__(self, obj: object):
        self.key = id(obj)
        self._track(obj)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, HashableWrapper):
            return self.key == other.key
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.key)

    def _track(self, obj: object) -> None:
        if self in _wrapper_to_obj:
            assert _wrapper_to_obj[self] is obj, (
                "There is already a wrapper for the provided object, but it's "
                "pointing to a different object. This is probably a bug, "
                "please report it."
            )
            return
        try:
            _wrapper_to_obj[self] = obj
        except TypeError as e:
            raise ObjectDoesNotSupportWeakRef(
                "The provided object does not support weak references. "
                "This is probably because it has a __slots__ attribute, "
                "but it does not have a __weakref__ slot. "
                "Please add the __weakref__ slot to the __slots__ class "
                "attribute."
            ) from e


_wrapper_to_obj: WeakValueDictionary[HashableWrapper, object] = WeakValueDictionary()
