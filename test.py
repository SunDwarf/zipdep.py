import yaml
import base64
from tornado import auth
try:
    from test2 import other_function
except ImportError as e:
    __test2_e = e
else:
    __test2_e = "this doesn't work in the test environment."

__zipdep_zipmodules = ["yaml", "base64", "tornado"]


def test():
    pass

if __name__ == "__main__":
    print("Loaded YAML from {}".format(yaml.__path__))
    print("base64, however, is a built-in, so it's loaded from {}".format(base64.__file__))
    print("We only imported a function from tornado, not the module. However, that's checked too! Tornado's auth module is",
          auth)
    print("However, since other_function is a project file, it won't import successfully outside of the test "
          "environment.")
    print("See:", __test2_e)
