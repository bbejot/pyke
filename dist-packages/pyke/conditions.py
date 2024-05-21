#!/bin/env python

from abc import ABC, abstractmethod


VALID = '__VALID__'
INVALID = '__INVALID__'
UPDATED = '__UPDATED__'


class Condition(ABC):
    @property
    @abstractmethod
    def uses_state_property(self):
        pass

    @abstractmethod
    def check(self):
        pass


class StatelessCondition(Condition):
    @property
    def uses_state_property(self):
        return False

    # not implemented: check


class StatefulCondition(Condition):
    @property
    def uses_state_property(self):
        return True

    @abstractmethod
    def update_state(self):
        pass

    # not implemented: check


