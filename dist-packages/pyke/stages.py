#!/bin/env python

from .errors import PykeException
from .utils import check_type, check_lst_type


# These variables are safe to grab after the user calls pyke.init
stages = ()
stages_by_name = {}
config = None
default_stage = None


class Stage:
    def __init__(self, name, is_target_default):
        self.name = name
        self.is_target_default = is_target_default
        self.targets = []

    def _add_target(self, target):
        self.targets.append(target)
    

class PreConfigStage(Stage):
    pass


class ConfigStage(Stage):
    pass


class PostConfigStage(Stage):
    pass


def _make_stages_by_name(stage_names, config_name, default_stage_name):
    global stages, stages_by_name, config, default_stage

    stages_by_name = {}
    before_config = True
    for name in stage_names:
        is_target_default = name == default_stage_name
        if name == config_name:
            stage = ConfigStage(name, is_target_default)
            before_config = False
        elif before_config:
            stage = PreConfigStage(name, is_target_default)
        else:
            stage = PostConfigStage(name, is_target_default)
        stages_by_name[name] = stage

    stages = tuple([
        stages_by_name[name]
        for name in stage_names
        ])
    config = None if config_name is None else stages_by_name[config_name]
    default_stage = None if default_stage_name is None else stages_by_name[default_stage_name]
    return stages


    set_stages(stages, config_stage, default_stage)

def make_stages_by_name(stage_names:list[str]|tuple[str], config_stage_name:str|None, default_stage_name:str|None):
    # this is not part of the public API, but the stages are all coming in by name
    if config_stage_name is not None and config_stage_name not in stage_names:
        raise PykeException(f'Config name ({config_stage_name}) must be one of the stages ({stage_names})')

    if default_stage_name is not None and default_stage_name not in stage_names:
        raise PykeException(f'Target default ({default_stage_name}) must be either None or one of the stages ({stage_names})')

    if len(stage_names) != len(set(stage_names)):
        raise PykeException(f'Cannot have repeating stages {stage_names})')

    return _make_stages_by_name(stage_names, config_stage_name, default_stage_name)


def get_stage(name):
    # TODO: check_types
    # TODO: public API documentation
    if name is None:
        stage = default_stage
    else:
        stage = stages_by_name[name]
    return stage 


def list_stages():
    # TODO: public API documentation
    return [stage.name for stage in stages]
