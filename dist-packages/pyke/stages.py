#!/bin/env python

import os

from .errors import PykeException
from .utils import check_type, check_lst_type, check_callable
from .target import Target
from .conditions import Condition


stages_by_name = {}
targets_by_name = {}
# These variables are safe to grab after the user calls pyke.init
stages = ()
config = None
default_stage = None


class Stage:
    def __init__(self, name):
        self.name = name
        self.targets = []  # append-only
        self.stage_target = Target(
            self.stage_target_name(self.name),
            action=None,
            args=(),
            kwargs={},
            dependencies=self.targets,  # important that this is a reference
            products=[],
            always_run=False)
        register_target(self.stage_target)

    def _add_target(self, target):
        self.targets.append(target)

    @staticmethod
    def stage_target_name(stage_name):
        return f'_pyke_{stage_name}-stage'
    

class PreConfigStage(Stage):
    pass


class ConfigStage(Stage):
    def __init__(self, name, workspace):
        super().__init__(name)
        self.workspace = workspace
        self.stage_init_target = Target(
            self.stage_target_name(name) + '-init',
            action=os.makedirs,
            args=(self.workspace,),
            kwargs={'exist_ok': True},
            dependencies=[],
            products=[self.workspace],
            always_run=False)
        register_target(self.stage_init_target)

    def workspace_exists(self):
        return os.path.isdir(self.workspace)

    def _add_target(self, target):
        super()._add_target(target)
        target.dependencies.append(self.stage_init_target)


class PostConfigStage(Stage):
    pass


def _make_stages_by_name(stage_names, config_name, default_stage_name, workspace):
    global stages, stages_by_name, config, default_stage

    stages_by_name = {}
    before_config = True
    for name in stage_names:
        if name == config_name:
            stage = ConfigStage(name, workspace)
            before_config = False
        elif before_config:
            stage = PreConfigStage(name)
        else:
            stage = PostConfigStage(name)
        stages_by_name[name] = stage

    stages = tuple([
        stages_by_name[name]
        for name in stage_names
        ])
    config = None if config_name is None else stages_by_name[config_name]
    default_stage = None if default_stage_name is None else stages_by_name[default_stage_name]
    return stages

    set_stages(stages, config_stage, default_stage)


def make_stages_by_name(stage_names:list[str]|tuple[str], config_stage_name:str|None, default_stage_name:str|None, workspace:str|None):
    # this is not part of the public API, but the stages are all coming in by name
    if config_stage_name is not None and config_stage_name not in stage_names:
        raise PykeException(f'Config name ({config_stage_name}) must be one of the stages ({stage_names})')

    if default_stage_name is not None and default_stage_name not in stage_names:
        raise PykeException(f'Target default ({default_stage_name}) must be either None or one of the stages ({stage_names})')

    if len(stage_names) != len(set(stage_names)):
        raise PykeException(f'Cannot have repeating stages {stage_names})')

    return _make_stages_by_name(stage_names, config_stage_name, default_stage_name, workspace)


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


def register_target(target):
    # all target names must be unique
    if target.name in targets_by_name:
        raise KeyError(f'Already have a target named "{name}"')
    
    targets_by_name[target.name] = target


def add_target(name, stage=None, action=None, args=(), kwargs={}, dependencies=[], products=[], always_run=False):
    """ add a target """
    # public function.  Check all inputs, convert names to objects
    check_type(name, 'name', str)
    check_type(stage, 'stage', (str, Stage, None))
    check_callable(action, 'action', allow_none=True)
    check_type(args, 'args', (tuple, list))
    check_type(kwargs, 'kwargs', dict)
    check_lst_type(dependencies, 'dependencies', (tuple, list), (str, Target, Condition))
    check_lst_type(products, 'products', (tuple, list), (str, Target, Condition))

    stage = get_stage(stage) if isinstance(stage, str) else stage
    dependencies = [get_target(dep) if isinstance(dep, str) else dep for dep in dependencies]
    products = [get_target(prod) if isinstance(prod, str) else prod for prod in products]
    
    target = Target(name, action, args, kwargs, dependencies, products, always_run)
    if stage is None:
        stage = default_stage
    stage._add_target(target)
    register_target(target)
    return target


def get_target(name):
    """ Get a target from its name. """
    # public function.  Check all inputs.
    # TODO: check types
    assert isinstance(name, str)
    return targets_by_name[name]


def list_targets():
    # TODO: document public API
    return sorted(list(targets_by_name.keys()))
