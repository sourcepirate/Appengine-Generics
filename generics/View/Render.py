__author__ = 'plasmashadow'

import json
import logging
import os
from google.appengine.ext.webapp import template

log = logging.getLogger(__name__)


class GenericViewException(Exception):
    pass


"""
Sorry for my convension i always use camelcase regard less of language.
"""


class Genericview(object):
    """New style Object class"""

    def __init__(self, template_path="/../../View/"):
        self.template_path = template_path

    def json_response(self, obj, type=None):
        res = None
        if type == "dict":
            res = json.dumps(obj)
        elif type == "object":
            res = json.dumps(obj.__dict__)
        else:
            raise GenericViewException("unable to render the view")
        self.response.headers["content_type"] = "application/json"
        self.response.write(res)

    def render_json(self, obj, type=None):
        self.json_response(self, obj, type=type)

    def render_html(self, htmlfilename, **kwargs):
        self.path = os.path.dirname(__file__)
        self.path += self.template_path
        self.response.headers["content_type"] = "text/html"
        templateContent = template.render(self.path + htmlfilename, kwargs)
        log.info(templateContent)
        self.response.out.write(templateContent)

    def render_text(self, txt):
        self.response.headers["content_type"] = "text/html"
        self.response.write(txt)

    def render_image(self, img):
        self.response.headers["content_type"] = "image/png"
        self.response.write(img)
