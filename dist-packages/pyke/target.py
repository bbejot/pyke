#!/bin/env python

from .errors import PykeException
from .conditions import Condition


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
        assert isinstance(dep, (Target, Condition))

        if dep in self.dependencies:
            raise  PykeException(f'Dependency {name} already added to {self.name}')
        self.dependencies.append(dep)

    def add_product(self, product):
        """ Add a product as being produced by this target. """
        # public function.  Check all inputs, convert names to objects
        if isinstance(product, str):
            product = get_target(product)
        assert isinstance(product, (Target, Condition))

        if product in self.products:
            raise  PykeException(f'Dependency {name} already added to {self.name}')
        self.products.append(product)

    def _act(self):
        if self.action is None:
            return None
        self.retval = self.action(*self.args, **self.kwargs)
        return self.retval
