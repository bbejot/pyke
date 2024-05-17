#!/bin/env python

import importlib.util
import inspect
import os
import sys

from .utils import path_split


pykefiles = {}


if '' not in importlib.machinery.SOURCE_SUFFIXES:
    importlib.machinery.SOURCE_SUFFIXES.append('')

def _import_pykefile(name, path):
    canonical_name = f'pyke.pykefiles.{name}'
    spec = importlib.util.spec_from_file_location(canonical_name, path) 
    mod = importlib.util.module_from_spec(spec)
    pykefiles[name] = mod
    sys.modules[canonical_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _import_nonroot_pykefile(path):
    root_dir = os.path.dirname(pykefiles['root'].__file__)
    child_dir = os.path.dirname(path)
    rel_path = os.path.relpath(child_dir, root_dir)
    mod_path = ['root'] + path_split(rel_path)
    mod_name = '.'.join(mod_path)
    mod = _import_pykefile(mod_name, path)
    return mod


def import_root_pykefile(path):
    return _import_pykefile('root', path)

    
def load(relpath):
    # TODO: check_types
    # TODO: public API documentation
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    parent_pykefile_path = module.__file__
    child_pykefile_path = os.path.join(os.path.dirname(parent_pykefile_path), relpath, 'Pykefile')
    _import_nonroot_pykefile(child_pykefile_path)
