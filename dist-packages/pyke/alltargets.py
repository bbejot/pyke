#!/bin/env python

from .conditions import Condition
from .stages import get_stage, Stage
from .target import Target
from .utils import check_type, check_lst_type, check_callable
from . import stages


targets_by_name = {}


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
    
    # all target names must be unique
    if name in targets_by_name:
        raise KeyError(f'Already have a target named "{name}"')
    
    target = Target(name, action, args, kwargs, dependencies, products, always_run)
    targets_by_name[name] = target
    if stage is None:
        stage = stages.default_stage
    stage._add_target(target)

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
