import webapp2
from google.appengine.ext import ndb
from google.appengine.ext.ndb import Cursor
from google.appengine.ext.ndb.model import IntegerProperty, \
                                           StringProperty, DateTimeProperty, \
                                           JsonProperty
from services.response_renderer import ResponseRenderer
import json
import logging

log = logging.getLogger(__name__)

class DatastoreEndpointException(Exception):

    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return "<%s>%s"%(self.__class__.__name__, self.message)


class DatastoreEndpoint(webapp2.RequestHandler, ResponseRenderer):

    """
      Restendpoint generation class
      that extends webapp2.RequestHandler
    """

    _model = None

    __defined = ["limit", "offset", "cursor"]

    def get(self, *args):

        id_defined = False

        if args and len(args) > 1:
            raise DatastoreEndpointException("disobeying rest convension /path/:id")
        elif args:
            id_defined = args[0]

        limit = int(self.request.get("limit", 10))
        offset = int(self.request.get("offset", 0))
        cursor = self.request.get("cursor", None)
        if cursor:
            cursor = Cursor(urlsafe=cursor)
        more = False

        log.info(self.request.params)

        if not id_defined:
            query_dict = {}
            for key, value in self.request.params.items():
                if key not in self.__defined:
                    query_dict.update([(key, value)])
            log.info(query_dict)
            query = _construct_query(self._model, query_dict)
            records, cursor, more = query.fetch_page(limit, start_cursor=cursor, offset=offset)
            query_dict = map(lambda x: x.to_dict(), records)

        else:
            entity = self._model.get_by_id(id_defined)
            self.render_json(entity.to_dict())
            return


        response_template = {
            "limit": limit,
            "offset": offset + len(records),
            "records": query_dict,
            "cursor": cursor.urlsafe() if cursor else None,
            "more": more
        }

        self.render_json(response_template)

    def post(self, *args):

        body = self.request.params
        try:
            new_model = self._model()
            id = body.get("id")
            parent = body.get("parent")

            if self._model.get_by_id(id):
                raise DatastoreEndpointException("Entity already there")

            for key, value in body.items():

                if key in ["id", "parent"]:
                    continue

                if isinstance(getattr(self._model, key), IntegerProperty):
                    value = int(value)
                if isinstance(getattr(self._model, key), JsonProperty):
                    value = json.loads(value)
                setattr(new_model, key, value)

            if not parent and id:
                new_model.key = ndb.Key(self._model, id)

            elif parent and id:
                new_model.key = ndb.Key(self._model, id, parent=ndb.Key(self._model, parent))

            new_model.put()
            self.render_json(new_model.to_dict())
        except Exception as e:
            log.info(str(e))
            self.response.set_status(500)
            self.render_json(dict(
                message=str(e.message)
            ))

    def put(self, *args):
        body = self.request.params
        id = body.get("id")

        try:
            if not id:
                raise DatastoreEndpointException("Id of element to be updated is not defined")

            model = self._model.get_by_id(id)

            if not model:
                raise DatastoreEndpointException("element to be updated not present")

            for key, value in body.items():
                if key in ["id", "parent"]:
                    continue

                if isinstance(getattr(self._model, key), IntegerProperty):
                    value = int(value)

                if isinstance(getattr(self._model, key), JsonProperty):
                    value = json.loads(value)

                setattr(model, key, value)

            model.put()
            self.render_json(model.to_dict())

        except Exception as e:
            self.response.set_status(500)
            self.render_json(dict(message=str(e.message)))


    def delete(self, id):

        log.info(id)
        body = self.request.params

        try:
            if not id:
                raise DatastoreEndpointException("Id of element to be updated is not defined")
            model = self._model.get_by_id(id)

            if not model:
                raise DatastoreEndpointException("element to be deleted not present")

            dct = model.to_dict()
            model.key.delete()
            self.render_json(model.to_dict())

        except Exception as e:
            self.response.set_status(500)
            self.render_json(dict(message=str(e.message)))


def generate_handler(model):

    endpoint = type('endpointclass', DatastoreEndpoint.__bases__, dict(DatastoreEndpoint.__dict__))
    setattr(endpoint, '_model', model)
    return endpoint


def _construct_query(model, query_dict):

    args = []
    for key, value in query_dict.items():
        args.append(ndb.AND(getattr(model, key) == value))
    query = model.query(*args)
    return query