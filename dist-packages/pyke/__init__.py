#!/bin/env python

from .errors import PykeException

VERSION = '0.1'
ALLOWED_VERSIONS = ['0.1']

def init(version):
    # This bit of convoluted nonsense dummy-proofs the API.  The API is hidden until
    # the user call init, then it appears.  This is also where some amount of version
    # controlling happens.
    from .target import get_target, add_target, list_targets
    from .stages import set_stages, get_stage, list_stages
    from .loader import load, pykefiles
    gbls = globals()
    if version == '0.1':
        gbls['get_target'] = get_target
        gbls['add_target'] = add_target
        gbls['list_targets'] = list_targets
        gbls['set_stages'] = set_stages
        gbls['get_stage'] = get_stage
        gbls['list_stages'] = list_stages
        gbls['load'] = load
        gbls['pykefiles'] = pykefiles
    else:
        assert version not in ALLOWED_VERSIONS
        raise PykeException(f'Unsupported version {version}.  Allowed: {ALLOWED_VERSIONS}')
