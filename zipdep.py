#!/usr/bin/env python
# ======================================================================================================================
#
# zipdep.py
#
# This allows you to package up all your dependencies into one big zipfile, which can then be imported from.
# It will automatically be shoved onto the front of the chosen file.
# To invoke, just run python -m zipdep <yourfile>.py.
# It will scan and attempt to locate all your dependencies, then zip them up, and encode it.
# You can import your dependencies as normal, and they will all be picked up.
# Make sure not to have any code running at the module level - this will be all executed when imported.
#
# ---
#
# Copyright (c) 2016 Isaac Dickinson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# ======================================================================================================================
import os
import zipfile
from types import ModuleType
import sys
try:
    from base91 import encode
    __b95_available = True
except ImportError:
    from base64 import b85encode as encode
    __b95_available = False

import importlib
import io
from collections import OrderedDict

# https://bugs.python.org/issue17004
# https://bugs.python.org/issue21751
# https://bugs.python.org/issue5950
#if hasattr(zipfile, "ZIP_LZMA"):
#    mode = zipfile.ZIP_LZMA
#elif hasattr(zipfile, "ZIP_BZIP2"):
#    mode = zipfile.ZIP_BZIP2
if hasattr(zipfile, "ZIP_DEFLATED"):
    mode = zipfile.ZIP_DEFLATED
else:
    mode = zipfile.ZIP_STORED

__version__ = "1.1.0"

uppertemplate = """#!/usr/bin/env python
# This file was partially generated by zipdep.py version {zd_version}
# For more information about zipdep.py, see https://github.com/SunDwarf/zipdep.py

# region zipdep
from base64 import b85decode as __zipdep_bdecode
import tempfile
import sys
import os
import struct

# Declare zip file.
# THIS IS VERY UGLY. YOU SHOULD NOT BE USING THIS FOR DEVELOPMENT. IT WILL BE NEAR IMPOSSIBLE.

__zipdep__zf = \"""
{zd_zipfile}
\"""

# Base91 implementation
# see: https://github.com/SunDwarf/base91-python/blob/master/base91/__init__.py
__zipdep__base91_alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                   'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                   'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                   'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                   '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '#', '$',
                   '%', '&', '(', ')', '*', '+', ',', '.', '/', ':', ';', '<', '=',
                   '>', '?', '@', '[', ']', '^', '_', '`', chr(123), '|', chr(125), '~', '"']

__zipdep__decode_table = dict((v, k) for k, v in enumerate(__zipdep__base91_alphabet))

def __zipdep_b91_decode(encoded_str):
 v=-1
 b=0
 n=0
 out=bytearray()
 for strletter in encoded_str:
  if not strletter in __zipdep__decode_table:
   continue
  c=__zipdep__decode_table[strletter]
  if(v<0):
   v=c
  else:
   v+=c*91
   b|=v<<n
   n+=13 if(v&8191)>88 else 14
   while True:
    out+=struct.pack('B',b&255)
    b>>=8
    n-=8
    if not n>7:
     break
   v=-1
 if v+1:
  out+=struct.pack('B',(b|v<<n)&255)
 return out

__zipdep_has_base91 = {zd_hasb91}

__zipdep__tmpdir = tempfile.mkdtemp()

def __zipdep__dextract():
    # Base85-decode the zf.
    if __zipdep_has_base91:
        d = __zipdep_b91_decode
    else:
        d = __zipdep_bdecode
    data = d(__zipdep__zf.replace("\\n", ""))
    # Create the zipfile in the temporary directory.
    with open(os.path.join(__zipdep__tmpdir, "zipdep.zip"), mode='wb') as f:
        f.write(data)
    # Update sys.path.
    sys.path.insert(0, os.path.join(__zipdep__tmpdir, "zipdep.zip"))

def __zipdep__cleanup():
    # Remove the zipdep.zip file
    os.remove(os.path.join(__zipdep__tmpdir, "zipdep.zip"))
    os.removedirs(__zipdep__tmpdir)

__zipdep__dextract()

# endregion

# ======================================================================================================================

"""

lowertemplate = """

# ======================================================================================================================
# Zipdep cleanup.
__zipdep__cleanup()
"""


def zipdir(path, ziph, name):
    # Walk over files
    if not os.path.isdir(path):
        print(os.path.join(name, path), "->", name)
        ziph.write(os.path.join(name, path), arcname=name + '.py')
    for root, dirs, files in os.walk(path):
        # Sanitize root
        newroot = '/'.join([_.lstrip("/") for _ in root.partition(name) if _][1:])
        if '__pycache__' in root:
            continue
        for file in files:
            ziph.write(os.path.join(root, file), arcname=os.path.join(newroot, file))
            pass


def extract_path(obj: ModuleType):
    # First, check if it has a __package__.
    if hasattr(obj, "__package__") and obj.__package__:
        print("found package: {}".format(obj.__package__))
        # If it's a top-level module...
        if obj.__package__ == obj.__name__:
            pass
        else:
            # Try and import the top-level package.
            try:
                mod = importlib.import_module(obj.__package__)
            except ImportError:
                print("unable to import module/package: {}".format(obj.__package__))
            else:
                print("found&imported module/package:", obj.__package__)
                # Recursively extract the path.
                path = extract_path(mod)
                if path:
                    # Return the package name instead of the submodule name.
                    return path, obj.__package__
    # Easy! We have a __path__ to get.
    if hasattr(obj, "__path__"):
        if len(obj.__path__) == 0:
            # oh, nevermind
            pass
        else:
            print("path:", obj.__path__[0])
            if not 'site-packages' in obj.__path__[0]:
                print("module {} appears to be stdlib, skipping".format(obj.__name__))
                return None
            else:
                return obj.__path__[0]
    # Also as easy.
    elif hasattr(obj, "__file__"):
        if obj.__file__ == "__zipdep":
            # wat
            return None
        print("path:", obj.__file__)
        if not 'site-packages' in obj.__file__:
            print("module {} appears to be stdlib/project file, skipping".format(obj.__name__))
            return None
        else:
            return obj.__file__
    else:
        print("(assuming builtin, no __path__/__file__)")
        return None


def __main__():
    # insert into path
    sys.path.insert(0, os.getcwd())
    # get argv
    if len(sys.argv) == 1:
        print("usage: zipdep file.py")
        sys.exit(1)
    filenames = sys.argv[1:]
    final_zipdep = sys.argv[1]
    # declare temporary dictionary
    loc = OrderedDict({"__name__": "__zipdep"})
    # exec() file
    for filename in filenames:
        if not os.path.exists(filename):
            print("skipping file {} - does not exist".format(filename))
        with open(filename) as f:
            try:
                exec(f.read(), {}, loc)
            except ImportError as e:
                print("seems like your modules weren't installed. error: {}".format(e))
                raise
    # scan locals
    modules = {}
    if "__zipdep_zipmodules" in loc:
        print("found `zipdep_zipmodules, loading modules from here instead of scanning")
        # Just load a list of modules from here.
        for mod in loc["__zipdep_zipmodules"]:
            print("importing {}".format(mod))
            md = importlib.import_module(mod)
            path = extract_path(md)
            if path:
                modules[mod] = (path, mod)
    else:
        for name, obj in loc.items():
            if isinstance(obj, ModuleType):
                print("found module:", name)
                path = extract_path(obj)
                if path:
                    if len(path) == 2:
                        modules[path[1]] = path
                    elif path:
                        modules[name] = (path, name)
            # next, check if it has a __module__, for things such as sub-level functions (from x import y)
            if hasattr(obj, "__module__"):
                print("found object: {} with __module__: {}".format(name, obj.__module__))
                if not obj.__module__:
                    print("skipping object in local scope")
                    continue
                # attempt to import
                if obj.__module__ in modules:
                    print("module already imported; skipping")
                try:
                    mod = importlib.import_module(obj.__module__)
                except ImportError:
                    print("unable to import module: {}".format(obj.__module__))
                else:
                    print("found&imported module:", obj.__module__)
                    path = extract_path(mod)
                    if path:
                        modules[name] = (path, name)
    print("constructing zipfile with modules: {}".format(
        ', '.join(["{} from {}".format(name, path[0]) for (name, path) in modules.items()])))
    # create in-memory zip
    in_mem_zip = io.BytesIO()
    # create zipfile
    zf = zipfile.ZipFile(in_mem_zip, mode='w', compression=mode)
    # zip up modules
    for mod, path in modules.items():
        print("zipping module", mod)
        zipdir(path[0], zf, path[1])
    # close && seek
    zf.close()
    in_mem_zip.seek(0)
    # encode in base85
    b85_data = encode(in_mem_zip.read())
    if isinstance(b85_data, bytes):
        b85_str = b85_data.decode()
    else:
        b85_str = b85_data
    b85_str = b85_str.replace("\"", "\\\"")
    b85 = '\n'.join([b85_str[i:i+80] for i in range(0, len(b85_str), 80)])
    # now the fun part
    templated = uppertemplate.format(zd_version=__version__, zd_zipfile=b85, zd_hasb91=__b95_available)
    in_mem_zip.close()
    # open file in r, read in contents, then re-open in 'w' to overwrite
    with open(final_zipdep) as f:
        contents = f.read()
    with open(final_zipdep + '.zipdep.py', 'w') as f:
        # Now save.
        f.write(templated + contents + lowertemplate)
    print("success! written to file {}".format(final_zipdep + ".zipdep.py"))


if __name__ == "__main__":
    __main__()
