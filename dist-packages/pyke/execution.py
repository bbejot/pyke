#!/bin/env python

from .target import get_target

_execd = set([])

def exec_target_by_name(name):
    if name in _execd:
        return
    _execd.add(name)
    
    target = get_target(name)
    for dep in target.dependencies:
        exec_target_by_name(dep.name)
    target._act()
