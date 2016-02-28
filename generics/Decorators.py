__author__ = 'plasmashadow'
import json

def singleton(PythonClass):
    """
    A Decorator which allows us to create only one instance of the class through out the program event thought it is
    instanciated many times in the program
     usage:
      @singleton
      class myclass:
         pass
    :param PythonClass: Is just the name of the class where the decorators is been actually called.
    :return:
    """
    _instances = {}
    def getInstance(*args, **kwargs):
        if PythonClass not in _instances:
            _instances[PythonClass] = PythonClass(*args,**kwargs)
        return _instances[PythonClass]
    return getInstance

def Json(func):
    """
    Function converts the response to json
    :param func: input to the function on which this decorator is used
    :return:
    """
    def inner(*args,**kwargs):
        data = func(*args,**kwargs)
        for key in data:
            data[key] = str(data[key])
        return json.dumps(data)
    return inner

def JsonResponse(f):
    """
    A helper method which helps to access the self parameter based on class method
    :param f: function that is passed to
    :return: None
    """
    def inner(self, *args, **kwargs):
        print args
        data = f(self, *args, **kwargs)
        for key in data:
            data[key] = str(data[key])
        self.response.write(json.dumps(data))
        return None
    return inner

