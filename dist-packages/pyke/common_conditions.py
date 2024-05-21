#!/bin/env python

from abc import ABC, abstractmethod

from .conditions import StatelessCondition, StatefulCondition
from .state import load_state, save_state, NO_STATE


class AbsPathExists(StatelessCondition):
    def __init__(self, path):
        expanded_path = os.path.expanduser(path)
        if not os.path.isabs(expanded_path):
            raise PykeException(f'AbsPathExists expects an absolute path, received {path}')
        self.path = expanded_path

    def check(self):
        return os.path.exists(self.path)


class FileExists(AbsPathExists):
    """ Checks to see if a file exists.  Note, file changes will not be detected.  For that use FileUnchanged. """
    def check(self):
        # note, follows links
        return os.path.isfile


class DirExists(AbsPathExists):
    """ Checks to see if a directory exists.  Note, changes to the directory or any of its contents will not be detected.  For that use FileUnchanged. """
    def check(self):
        # note, follows links
        return os.path.isdir(self.path)


class FindablePath(StatelessCondition):
    def __init__(self, rel_path, search_dirs):
        # TODO: add an option for ignoring relative search dirs
        expanded_rel_path = os.path.expanduser(rel_path)
        if os.isabs(expanded_rel_path):
            raise PykeException(f'FindablePath expects a relative path, got {rel_path}')
        self.path = expanded_rel_path
        expanded_search_dirs = []
        for search_dir in search_dirs:
            expanded_search_dir = os.path.expanduser(search_dir)
            if not os.path.isabs(expanded_search_dir):
                raise PykeException(f'FindablePath expects absolute search dirs, got {search_dir}')
            expanded_search_dirs.append(expanded_search_dir)
        self.search_dirs = expanded_search_dirs

    def full_paths(self):
        return [os.path.join(base_dir, self.rel_path) for base_dir in self.search_dirs]

    def existing_paths(self):
        return [
            abs_path
            for abs_path in self.full_paths()
            if os.path.exists(abs_path)
            ]

    def check(self):
        return len(self.existing_paths()) > 0


class ExecutableOnPath(FindablePath):
    """ Checks to see if an executable is findable on the sys.path variable """
    def __init__(self, rel_path):
        super().__init__(rel_path, sys.path)

    def executables(self):
        # TODO: check to make sure this works in Windows
        return [
            abs_path
            for abs_path in self.existing_paths()
            if os.path.isfile(abs_path)
            and os.access(abs_path, os.X_OK)
            ]

    def check(self):
        return len(self.executables()) > 0


class UnchangedCondition(StatefulCondition):
    def __init__(self, state_name):
        self.state_name = state_name

    @abstractmethod
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
