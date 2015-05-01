__author__ = 'plasmashadow'

from google.appengine.api import memcache

class Memcache:
    @staticmethod
    def get(key):
        return memcache.get(str(key))
    @staticmethod
    def set(key, value, time):
        memcache.set(str(key), value, time)
    @staticmethod
    def delete(key):
        memcache.delete(str(key))