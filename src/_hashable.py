from __future__ import annotations

from collections.abc import Hashable
from weakref import WeakValueDictionary


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
        _wrapper_to_obj[self] = obj


_wrapper_to_obj: WeakValueDictionary[HashableWrapper, object] = WeakValueDictionary()
