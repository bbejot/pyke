#!/bin/env python

from .errors import PykeException

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


# These variables are voided after the user calls set_stages.
stages = ()
stages_by_name = {}
config = None
target_default = None

def _set_stages(stage_names, config_name, target_default_name):
    global stages, stages_by_name, config, target_default

    stages_by_name = {}
    before_config = True
    for name in stage_names:
        is_target_default = name == target_default_name
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
    config = stages_by_name[config_name]
    target_default = stages_by_name[target_default_name]
    return stages


def set_stages(stage_names, config, target_default):
    # TODO: check_types
    # TODO: public API documentation
    assert isinstance(stage_names, (list, tuple))
    assert all([isinstance(name, str) for name in stage_names])
    assert isinstance(config, str)
    assert isinstance(target_default, str)

    if config not in stage_names:
        raise PykeException(f'Config name ({config}) must be one of the stages ({stage_names})')

    if target_default is not None and target_default not in stage_names:
        raise PykeException(f'Target default ({target_default}) must be either None or one of the stages ({stage_names})')

    if len(stage_names) != len(set(stage_names)):
        raise PykeException(f'Cannot have repeating stages {stage_names})')

    return _set_stages(stage_names, config, target_default)


def get_stage(name):
    # TODO: check_types
    # TODO: public API documentation
    if name is None:
        stage = target_default
    else:
        stage = stages_by_name[name]
    return stage 


def list_stages():
    # TODO: public API documentation
    return [stage.name for stage in stages]
