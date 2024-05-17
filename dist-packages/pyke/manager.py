#!/bin/env python

from .errors import PykeException
from .stages import StageManager
from .targets import TargetManager
from .pykefiles import PykefileManager

class PykeManager:
    VERSION = '0.1'
    def __init__(self, version):
        self.ACTING_VERSION = version
        self.root = None
        self._stageman = StageManager()
        self._targetman = TargetManager(stageman)
        self._pykefileman = PykefileManager()
        self._initialized = False

    def init(version):
        if self._initialized:
            raise PykeException('Must call pyke.init only once!')
        self._initialized = True
        
        # add the public methods
        # TODO: remove this line after adding support for multiple versions
        assert version == '0.1'
        self.set_stages = self._stageman.set_stages
        self.get_stage = self._stageman.get_stage
        self.load = self._pykefileman.load
        self.add_target = self._targetman.add_target
        self.get_target = self._targetman.get_target
        return self.get_instance()

    def get_instance(self):
        if not self._initialized:
            raise PykeException('Must call pyke.init before calling pyke.get_instance!')
        return self


init, get_instance = (lambda pykeman: (pykeman.init, pykeman.get_instance))(PykeManager())
