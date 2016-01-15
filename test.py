import yaml
import base64
from tornado import auth

def test():
    pass

print("Loaded YAML from {}".format(yaml.__path__))
print("base64, however, is a built-in, so it's loaded from {}".format(base64.__file__))
print("We only imported a function from tornado, not the module. However, that's checked too! Tornado's auth module is",
      auth)
