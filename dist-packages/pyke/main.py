#!/bin/env python

import importlib
import os
import sys
import traceback

from . import utils
from . import execution
from . import loader

def main(raw_exec_dir):
    try:
        exec_dir = utils.resolve_path(raw_exec_dir)
        loader.load_root(exec_dir)
        # TODO: parse the input with argparse here
        for targetname in sys.argv[1:]:
            execution.exec_target_by_name(targetname)
    except:  # this is the only allowed bare except
        #traceback.print_exc()
        raise
        



if __name__ == '__main__':
    main(os.path.abspath('.'))
