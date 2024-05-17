#!/bin/env python

from types import NoneType

from .errors import PykeException
from .path import Path
from .stages import get_stage, Stage
from .utils import check_type, check_lst_type, check_callable
from . import stages

targets_by_name = {}

class Target:
    def __init__(self, name, action, args, kwargs, dependencies, products, always_run):
        self.name = name
        self.action = action
        self.args = args
        self.kwargs = kwargs
        self.dependencies = dependencies
        self.products = products
        self.always_run = always_run
        self.retval = None

    def add_dependency(self, dep):
        """ Add a dependency that must exist or run before this target. """
        # public function.  Check all inputs, convert names to objects
        if isinstance(dep, str):
            dep = get_target(dep)
        assert isinstance(dep, (Target, Path))

        if dep in self.dependencies:
            raise  PykeException(f'Dependency {name} already added to {self.name}')
        self.dependencies.append(dep)

    def add_product(self, product):
        """ Add a product as being produced by this target. """
        # public function.  Check all inputs, convert names to objects
        if isinstance(product, str):
            product = get_target(product)
        assert isinstance(product, (Target, Path))

        if product in self.products:
            raise  PykeException(f'Dependency {name} already added to {self.name}')
        self.products.append(product)

    def _act(self):
        if self.action is None:
            return None
        self.retval = self.action(*self.args, **self.kwargs)
        return self.retval


def add_target(name, stage=None, action=None, args=(), kwargs={}, dependencies=[], products=[], always_run=False):
    """ add a target """
    # public function.  Check all inputs, convert names to objects
    check_type(name, 'name', str)
    check_type(stage, 'stage', (str, Stage, NoneType))
    check_callable(action, 'action', allow_none=True)
    check_type(args, 'args', (tuple, list))
    check_type(kwargs, 'kwargs', dict)
    check_lst_type(dependencies, 'dependencies', (tuple, list), (str, Target, Path))
    check_lst_type(products, 'products', (tuple, list), (str, Target, Path))

    stage = get_stage(stage) if isinstance(stage, str) else stage
    dependencies = [get_target(dep) if isinstance(dep, str) else dep for dep in dependencies]
    products = [get_target(prod) if isinstance(prod, str) else prod for prod in products]
    
    # all target names must be unique
    if name in targets_by_name:
        raise KeyError(f'Already have a target named "{name}"')
    
    target = Target(name, action, args, kwargs, dependencies, products, always_run)
    targets_by_name[name] = target
    if stage is None:
        stage = stages.target_default
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
