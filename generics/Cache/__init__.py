__author__ = 'plasmashadow'

from google.appengine.api import memcache
from .im_cache import Cache as IMCache
from .mm_cache import MMCache

class Memcache:
    @staticmethod
    def get(key):
        return memcache.get(str(key))
    @staticmethod
    def set(key, value, time=24*60*60):
        memcache.set(str(key), value, time)
    @staticmethod
    def delete(key):
        memcache.delete(str(key))
