class MethodiCacheException(Exception):
    """Base class for all exceptions in this module."""


class ObjectDoesNotSupportWeakRef(TypeError, MethodiCacheException):
    """The provided object does not support weak references."""
