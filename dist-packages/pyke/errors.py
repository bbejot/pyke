#!/bin/env python

class PykeException(Exception):
    pass

class PykeTypeException(PykeException, TypeError):
    pass
