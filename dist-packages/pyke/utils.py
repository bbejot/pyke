#!/bin/env python

import os
from types import NoneType

from .errors import PykeTypeException


def resolve_path(raw_path):
    return os.path.abspath(os.path.expanduser(raw_path))


def path_split(path):
    """ splits a path into a list """
    if path == '':
        return []
    d, b = os.path.split(path)
    if d == '':
        return [b]
    if b == '':
        return [d]
    return path_split(d) + [b] 


def check_type(var, name, types):
    if not isinstance(types, tuple):
        types = (types,)

    objs = tuple(t for t in types if type(t) is not type)
    types = tuple(t for t in types if type(t) is type)

    if not isinstance(var, types) and var not in objs:
        raise PykeTypeException(f'Expected {name} to be of type {types}, was of type {type(var)}')


def check_lst_type(lst, lst_name, lst_types, ele_types):
    check_type(lst, lst_name, lst_types)
    ele_name = f'elements of {lst_name}'
    for ele in lst:
        check_type(ele, ele_name, ele_types)


def check_callable(var, name, allow_none=False):
    if callable(var):
        return
    if allow_none and var is None:
        return
    raise PykeTypeException(f'Expected {name} to be callable')


def all_or_nothing(*objs):
    """ Checks to see if either all of the objects are None or none of the objects are None. """
    # Seems like we need this in a couple places.  Might as well codify it
    return all([obj is None for obj in objs]) or all([obj is not None for obj in objs])
    
