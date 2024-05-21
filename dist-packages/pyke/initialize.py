#!/bin/env python

from .errors import PykeException
from .stages import make_stages_by_name, get_stage, list_stages, get_target, add_target, list_targets
from .loader import load, pykefiles
from .utils import check_type, check_lst_type
from .state import save_state, load_state


ALLOWED_VERSIONS = ('0.1')
initialized = False


def inner_init(version: str, stages:list[str]|tuple[str], config_stage:str|None, default_stage:str|None, workspace:str|None):
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
    check_type(workspace, 'workspace', (str, None))

    if (config_stage is None and workspace is not None) or (workspace is None and config_stage is not None):
        raise PykeException('config_stage and workspace must either be both None or both set')

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
            'save_state': save_state,
            'load_state': load_state,
        }
    else:
        assert version not in ALLOWED_VERSIONS
        raise PykeException(f'Unsupported version {version}.  Allowed: {ALLOWED_VERSIONS}')

    make_stages_by_name(stages, config_stage, default_stage, workspace)

    return api
