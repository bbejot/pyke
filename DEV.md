# General Guidance

## One pyke Per Process

If you want to call pyke from pyke, that's fine, just do it in a new process.  Much depends on this assumption - specifically the use of globals with functional programming over singletons with OOP.

## Functional Programming

Generally, a functional programming style is used.  Globals are ok, but don't overdo it.  Classes and objects are also ok, but don't overdo it.  Store things in standard collections if possible.

## API-minimal

Keep the API small, idiot-proof, transparent, and simple.  KISS the API.

Most things should be callable from "pyke".  e.g. "import pyke; pyke.add_target(...)".

Anything that is non-standard should have an explanation with it, and good justification for its existence.

# Conventions

## Relative imports for in-module use

All imports of pyke module files should be relative from the pyke folder.

## Import only what you need

Absolutely no glob (\*) imports!  Import either just the module or only the functions / classes you need.  Do not import objects - reference them from the module.

## Users can pass in objects or names of objects as str.  Internally, sling around objects.

Publicly facing functions should allow either objects to be passed in, or the name of that object to be passed in.  The function should check if the variable is a str, and then look up the object by name if so.

Internal-only functions should pass around the objects themselves and should not need to check if the object is a str.

## The entirety of the public API is in pyke/__init__.py

All of the public API should be in pyke/__init__.py.  It should be defined elsewhere, of course, and imported in.

## Members starting with \_ are private to that class / module

Private members indicate that its use should be within that module or class only.  It does NOT mean "private from the user".  Everything is private from the user except what is exposed in pyke/__init__.py.  "Public" members (that don't start with \_) are expected to be called from other modules, and should not be assumed to be part of the public API.
