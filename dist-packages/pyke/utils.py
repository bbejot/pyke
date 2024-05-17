#!/bin/env python

import os

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
    if not isinstance(var, types):
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
