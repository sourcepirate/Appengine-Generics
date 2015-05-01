__author__ = 'plasmashadow'

import webapp2
from View import Render



class Http(webapp2.RequestHandler, Render.Genericview):
    """
       Used as an Abstact class for deriving basic request and response Handlers
    """
    pass

class Router(object):
    """
    Primaryly used as flask router for
    app_engine applications.
    NOTE: Untested.
    """
    _routes = []
    @classmethod
    def add_route(cls, path, class_name):
        cls._routes.append((path, class_name))
