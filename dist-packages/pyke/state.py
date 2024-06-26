#!/bin/env python

import json
import os

from . import stages
from .errors import PykeException
from .utils import all_or_nothing


# For now, we maintain parity between the _state object and what is saved
# on disk at _pykecache_path.  This may become an issue later, at which point
# we can split things up.
# TODO: don't write the entire state every time


NO_STATE:str = '__NO_STATE__'
_state:dict|None = None
_pykecache_path:str|None = None


def _init():
    global _state, _pykecache_path
    assert all_or_nothing(_state, _pykecache_path)
    if stages.config is None:
        raise PykeException(f'The config stage is not defined: cannot access state')
    if not stages.config.workspace_exists():
        raise PykeException(f'The workspace directory does not exist: cannot access state')
        
    if _state is not None:
        # already initialized
        return

    _pykecache_path = os.path.join(stages.config.workspace, 'PykeCache.json')

    if os.path.exists(_pykecache_path):
        _read_state()
    else:
        _state = {
                'user': {},
                'pyke': {},
                }
        _write_state()


def _write_state():
    global _state, _pykecache_path
    assert _pykecache_path is not None
    assert _state is not None
    with open(_pykecache_path, 'w') as fd:
        json.dump(_state, fd, indent=2)


def _read_state():
    global _state, _pykecache_path
    assert _pykecache_path is not None
    assert _state is None
    with open(_pykecache_path, 'r') as fd:
        _state = json.load(fd)


def save_state(name:str, item:object, namespace:str='user'):
    _init()
    _state[namespace][name] = item
    # maintaining parity in an inefficient way
    # TODO: make it not O(n^2).  Preferably better.
    _write_state()


def load_state(name:str, default=KeyError, namespace:str='user'):
    _init()

    if default is not KeyError and name not in _state[namespace]:
        # PARITY, I SAY!
        save_state(name, default, namespace)

    return _state[namespace][name]
