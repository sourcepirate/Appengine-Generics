from google.appengine.api import memcache
import sys


class AdaptiveMemoryError(Exception):
    pass


class AdaptableMemory(object):
    _adaptive_max = 1024 * 2 * 1024

    def __init__(self):
        self.cache = memcache
        self.total_size = 0
        self.keys = set()

    def delete(self, key):
        return self.cache.delete(key)

    def _add(self, key, value):
        computed_size = sys.getsizeof(value)
        if not computed_size < self._adaptive_max:
            raise AdaptiveMemoryError("Exceed size more than 2MB")

        while not (computed_size+self.total_size < self._adaptive_max):
            key_del = self.keys.pop(0)
            value_del = self.cache.get(key)
            size_del = sys.getsizeof(value_del)
            self.cache.delete(key_del)
            self.total_size -= size_del
        self.keys.add(key)
        self.cache.set(key, value)

    def add(self, key, value):
        self._add(key, value)

    def get(self, key):
        return self.cache.get(key)


def default_decorator(func, *args, **kwargs):
    """
      Takes in a default decorator
      function
    """

    return repr((func, args, kwargs))


class MMCache(object):

    _cached = AdaptableMemory()

    @classmethod
    def cached(cls, kernal=default_decorator):
        def decorator(func):
            def inner(*args, **kwargs):
                key = kernal(func, *args, **kwargs)
                value = cls._cached.get(key)
                if not value:
                    value = func(*args, **kwargs)
                    cls._cached.add(key, value)
                return value
            return inner
        return decorator