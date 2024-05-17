#!/bin/env python

import importlib
import os
import sys

from . import utils
from . import execution
from . import loader

def main(raw_exec_dir):
    exec_dir = utils.resolve_path(raw_exec_dir)
    pykefile_path = os.path.join(exec_dir, 'Pykefile')
    if os.path.isfile(pykefile_path):
        pykefile_lib = loader.import_root_pykefile(pykefile_path)
    else:
        print('no Pykefile!')
    # TODO: parse the input with argparse here
    for targetname in sys.argv[1:]:
        execution.exec_target_by_name(targetname)


if __name__ == '__main__':
    main(os.path.abspath('.'))
