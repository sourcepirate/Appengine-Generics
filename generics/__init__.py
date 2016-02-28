__author__ = 'plasmashadow'

import webapp2, logging, os
from generics.View import Render
import json
from google.appengine.ext.webapp import template
from webapp2 import redirect as webapp2redirect
from datetime import datetime

log = logging.getLogger(__name__)


class Http(webapp2.RequestHandler, Render.Genericview):
    """
       Used as an Abstact class for deriving basic request and response Handlers
    """
    pass


class render(object):

    """
       Can be used as the base view function of webapp2 microframework.
    """

    def __init__(self, filename, **kwargs):

        """
          Tries to load the filename of the specific content type with
          the view folder.
        :param filename:
        :param kwargs:
        :return:
        """

        self.content_type = kwargs.pop("content_type",  "text/html")
        self.filename = filename
        self.kwargs = kwargs
        self.path = os.path.dirname(__file__)
        self.template_path = kwargs.pop("template_path", "/../View/")
        self.template_path = self.path + self.template_path
        self.cookies = kwargs.pop("cookies", {})

    @property
    def content(self):
        """
          Helps to the get the content of the specifed file through
          the tempalte loader.
        :return: the template content
        """

        template_content = template.render(self.template_path+self.filename, self.kwargs)
        return template_content

    @property
    def response(self):
        rv = webapp2.Response(self.content, content_type=self.content_type)
        for key, value in self.cookies.items():
            rv.set_cookie(key, value)
        return rv


class redirect(object):

    def __init__(self, route):
        self.route = route


from google.appengine.ext.ndb import Key
from google.appengine.ext.ndb import Model


class AppengineJSONEncoder(json.JSONEncoder):

    def default(self, obj):

        if isinstance(obj, datetime):
            return int((obj - datetime(1970, 1, 1)).total_seconds() * 1000)
        if isinstance(obj, Key):
            return obj.urlsafe()
        if isinstance(obj, Model):
            return obj.to_dict()
        return None


class Appengine(webapp2.WSGIApplication):

    def __init__(self, *args, **kwargs):
        super(Appengine, self).__init__(*args, **kwargs)
        self.router.set_dispatcher(self.__class__.custom_dispatcher)
        self.template_path = kwargs.get("template_path")

    @staticmethod
    def custom_dispatcher(router, request, response):
        rv = router.default_dispatcher(request, response)
        log.info(request)
        if isinstance(rv, basestring):
            rv = webapp2.Response(rv)
        elif isinstance(rv, tuple):
            rv = webapp2.Response(*rv)
        elif isinstance(rv, dict):
            rv = webapp2.Response(json.dumps(rv), content_type="application/json")

        elif isinstance(rv, render):
            rv = rv.response
            # data = rv.content
            # rv = webapp2.Response(data, content_type=rv.content_type)
        elif isinstance(rv, redirect):
            rv = webapp2.redirect(rv.route, request=request, response=response)
        elif isinstance(rv, webapp2.Response):
            return rv
        elif isinstance(rv, (list, Model)):
            rv = webapp2.Response(json.dumps(rv, cls=AppengineJSONEncoder), content_type="application/json")
        log.info(rv)
        return rv

    def route(self, *args, **kwargs):
        def wrapper(func):
            self.router.add(webapp2.Route(handler=func, *args, **kwargs))
            return func
        return wrapper