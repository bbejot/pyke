#!/bin/env python

from abc import ABC, abstract_method

from .state import load_state, save_state, NO_STATE


VALID = '__VALID__'
INVALID = '__INVALID__'
UPDATED = '__UPDATED__'


class Condition(ABC):
    @property
    @abstract_method
    def uses_state_property(self):
        pass

    @abstract_method
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

    @abstract_method
    def update_state(self):
        pass

    # not implemented: check


class UnchangedCondition(StatefulCondition):
    def __init__(self, state_name):
        self.state_name = state_name

    @abstract_method
    def calc_state(self):
        pass

    def check(self):
        cur_state = self.calc_state()
        if cur_state == NO_STATE:
            return INVALID
        prev_state = load_state(self.state_name)
        if prev_state == NO_STATE:
            return INVALID
        return VALID if cur_state == prev_state else INVALID

    def update_state(self):
        save_state(self.state_name, self.calc_state())


class FileUnchanged(UnchangedCondition):
    def __init__(self, path):
        self.path = path
        super().__init__(f'pyke.conditions.FileUnchanged(self.path)')

    def calc_state(self):
        if not os.path.isfile(self.path):
            return NO_STATE
        
        # TODO: do we want ctime so that file-permission changes invalidate files?
        # TODO: do we care if the link changes?
        # TODO: figure out how to give the user the option to hash the file contents
        return (
            os.stat(self.path),
            os.islink(self.path),
            )


class DirUnchanged(UnchangedCondition):
    # Recursive form.  Records state of the entire tree starting at a directory
    # Note that links are followed when determining the tree
    def __init__(self, path):
        self.path = path
        super().__init__(f'pyke.conditions.DirUnchanged(self.path)')

    def calc_state(self):
        if not os.path.isdir(self.path):
            return NO_STATE
        
        # TODO: do we want ctime so that file-permission changes invalidate files?
        # TODO: do we care if the link changes?
        # TODO: figure out how to give the user the option to hash the file contents

        state = []
        for dirpath, dirnames, filenames in os.path.walk(self.path, followlinks=True):
            for basename in filenames + [dirpath]:
                curpath = os.path.join(dirpath, basename)
                state.append(curpath, os.path.isdir(curpath), os.path.isfile(curpath), os.path.islink(curpath), os.stat(curpath).st_mtime)

        return tuple(state)
