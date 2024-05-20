#!/bin/env python

import importlib.util
import inspect
import os
import sys

from .errors import PykeException
from .utils import path_split


# This object is part of the public API.  As such, the user may grab references to it.
# We can modify it, but not reassign it.
pykefiles = {}

# This allows us to import "Pykefile" files
for end in ('', '.pyke'):
    if end not in importlib.machinery.SOURCE_SUFFIXES:
        importlib.machinery.SOURCE_SUFFIXES.append(end)


def _import_pykefile(pykefile_name, path):
    if pykefile_name in pykefiles:
        return pykefiles[pykefile_name]
    mod_name = f'pyke.{pykefile_name}'
    spec = importlib.util.spec_from_file_location(mod_name, path) 
    mod = importlib.util.module_from_spec(spec)
    pykefiles[pykefile_name] = mod
    # we have to put it in sys.modules in order for inspect.getmodule to find it
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _find_pykeroot(exec_dir):
    cur_dir = exec_dir
    while True:
        pykeroot_path = os.path.join(cur_dir, 'Pykeroot')
        if os.path.isfile(pykeroot_path):
            return pykeroot_path
        up_one_dir = os.path.dirname(cur_dir)
        if up_one_dir == cur_dir:
            raise PykeException(f'Could not find Pykeroot in {exec_dir} or in any of its ancestors')
        cur_dir = up_one_dir


def load_root(exec_dir):
    pykeroot_path = _find_pykeroot(exec_dir)
    return _import_pykefile('root', pykeroot_path)

    
def _find_pykefile_path(search_dir, relpath):
    default_pykefile_path = os.path.join(search_dir, relpath, 'Pykefile')
    pykeext_path = os.path.join(search_dir, relpath + '.pyke')
    default_pykefile_isfile = os.path.isfile(default_pykefile_path)
    pykeext_isfile = os.path.isfile(pykeext_path)
    if default_pykefile_isfile and pykeext_isfile:
        raise PykeException(f'Pyke file name collision between {default_pykefile_path} and {pykeext_path}')
    elif default_pykefile_isfile:
        pykefile_path = default_pykefile_path
    elif pykeext_isfile:
        pykefile_path = pykeext_path
    else:
        raise PykeException(f'Cannot load {relpath}, no Pykefile found')
    return pykefile_path


def load(relpath):
    """ relpath is a path with slashes in it, not dots.  Paths get turned into 
    module names, so paths with characters outsie of [a-zA-Z0-9_] may make things
    a little funky.

    TODO: Figure out if we want to filter these characters or let them
    pass through
    """
    # TODO: check_types
    # TODO: public API documentation
    frame = inspect.stack()[1]
    parent_mod = inspect.getmodule(frame[0])
    
    search_dir = os.path.dirname(parent_mod.__file__)
    pykefile_path = _find_pykefile_path(search_dir, relpath)

    relname = '.'.join(path_split(relpath))
    pykefile_name = f'{parent_mod.__name__}.{relname}'
    return _import_pykefile(pykefile_name, pykefile_path)
