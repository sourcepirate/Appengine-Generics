import re
from google.appengine.ext import ndb

class SaftStringProperty(ndb.StringProperty):
    """takes in a regex pattern to validate the property"""
    def __init__(self, *args, **kwargs):
        self.regex = kwargs.get('regex', '.*')
        super(SaftStringProperty, self).__init__(*args, **kwargs)

    def _validate(self, value):
        _match = re.search(self.regex)
        if not _match:
            raise TypeError(str(value) + " Is not a valid property")