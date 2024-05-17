#!/bin/env python

from .errors import PykeException

VERSION = '0.1'

def init(version: str, stages:list[str]|tuple[str]=['default'], config_stage:str|None=None, default_stage:str|None='default'):
    # This bit of convoluted nonsense dummy-proofs the API.  The API is hidden until
    # the user call init, then it appears.
    from .initialize import inner_init
    api = inner_init(version, stages, config_stage, default_stage)
    globals().update(api)
