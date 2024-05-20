#!/bin/env python

from .errors import PykeException
from .target import get_target, add_target, list_targets
from .stages import make_stages_by_name, get_stage, list_stages
from .loader import load, pykefiles
from .utils import check_type, check_lst_type


ALLOWED_VERSIONS = ('0.1')
initialized = False


def inner_init(version: str, stages:list[str]|tuple[str], config_stage:str|None, default_stage:str|None, cache_dir:str|None):
    global initialized
    if initialized:
        raise PykeException('Cannot call pyke.init more than once')
    else:
        initialized = True

    # param checking happens in this function even though it is not in the public API
    check_type(version, 'version', str)
    check_lst_type(stages, 'stages', (list, tuple), str)
    check_type(config_stage, 'config_stage', (str, None))
    check_type(default_stage, 'default_stage', (str, None))
    check_type(cache_dir, 'cache_dir', (str, None))

    if (config_stage is None and cache_dir is not None) or (cache_dir is None and config_stage is not None):
        raise PykeException('config_stage and cache_dir must either be both None or both set')

    # version controlling basically happens here
    if version == '0.1':
        api = {
            'get_target': get_target,
            'add_target': add_target,
            'list_targets': list_targets,
            'get_stage': get_stage,
            'list_stages': list_stages,
            'load': load,
            'pykefiles': pykefiles,
        }
    else:
        assert version not in ALLOWED_VERSIONS
        raise PykeException(f'Unsupported version {version}.  Allowed: {ALLOWED_VERSIONS}')

    make_stages_by_name(stages, config_stage, default_stage)

    return api
