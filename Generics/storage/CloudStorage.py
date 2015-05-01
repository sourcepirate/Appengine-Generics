__author__ = 'plasmashadow'

import cloudstorage as gcs
from google.appengine.api import app_identity
from uuid import uuid4
import logging

log = logging.getLogger(__name__)

retry_params = gcs.RetryParams(initial_delay=0.2, max_delay=5.0, backoff_factor=2, max_retry_period=15)
gcs.set_default_retry_params(retry_params)

class GoogleFile(object):

    def __init__(self, name, content_type=None):
        self.name = name
        self.content_type = "text/plain"
        self.file_id = str(uuid4())
        self.file = None
        self.__modes = {'w': {content_type: self.content_type}, 'r': {}}
        self.name = ("/" + app_identity.get_default_gcs_bucket_name() + "/" + self.name)

    def open(self):
        self.file = gcs.open(self.name, 'w')
        self.file.close()

    @staticmethod
    def _read_in_chunks(f, chunk_size=1024):
        data = f.read(chunk_size)
        while True:
            if not data:
                break
            yield data

    def write(self, data, append=False):
        t_data = ""
        file = None
        if append:
            file = gcs.open(self.name, 'r')
            str_list = file.read().split("\n")
            log.info(str_list)
            for piece in str_list:
                t_data = t_data + piece + "\n"
                log.info(t_data)
            file.close()
        if hasattr(data, '__iter__'):
            for item in data:
                t_data = t_data + str(item) +"\n"
        elif isinstance(data, str):
            t_data = t_data + str(data)
        else:
            t_data = t_data + str(data)
        file = gcs.open(self.name, 'w', content_type=self.content_type)
        file.write(t_data)
        file.close()

    def read(self):
        file = gcs.open(self.name, 'r')
        data = ""
        for piece in GoogleFile._read_in_chunks(file):
            data = data+piece
        file.close()
        return data




class Storage(object):
    """
    A config object which acts as a abstract class for storage
    """

    def __init__(self):
        self.storage_bucket = app_identity.get_default_gcs_bucket_name()
        self.files = {}

    @property
    def storage_bucket_name(self):
        return self.storage_bucket

    @storage_bucket_name.setter
    def storage_bucket_name(self,value):
        if isinstance(value,str):
            self.storage_bucket = value
        else:
            raise TypeError("Invalid name of bucket")
