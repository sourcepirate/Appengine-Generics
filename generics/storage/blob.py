from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
import webapp2, uuid


class Binary(ndb.Model):
    name = ndb.StringProperty(required=True)
    path = ndb.StringProperty(required=True, default="/")
    key = ndb.BlobKeyProperty(required=True)
    prefix = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)


class Bucket(ndb.Model):
    name = ndb.StringProperty()
    files = ndb.KeyProperty(Binary, repeated=True)
    prefix = ndb.StringProperty(default=str(uuid.uuid4()))

    @ndb.tasklet
    def get_binary(self, name):
        prefix = self.prefix
        name = name.lower()
        key = "{}_{}".format(prefix, name)
        bin = yield self.__class__.get_by_id_async(key)
        raise ndb.Return(bin)

    @ndb.tasklet
    def create_binary(self, name, key, path="/"):
        name = name.lower()
        prefix = self.prefix
        key_value = "{}_{}".format(prefix, name)
        item = self.get_binary(name)
        if not item:
            binary = Binary(id=key_value)
            binary.path = path.lower()
            binary.prefix = prefix
            binary.name = name
            binary.key = key
            bin = yield binary.put_async()
            raise ndb.Return(bin)
        raise ndb.Return(None)

    @ndb.tasklet
    def get_by_path(self, path):
        prefix = self.prefix
        query = Bucket.query(ndb.AND(Bucket.prefix == prefix, Bucket.path == path.lower()))
        results = yield query.fetch_async()
        raise ndb.Return(results)