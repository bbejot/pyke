# General Guidance

## One pyke Per Process

If you want to call pyke from pyke, that's fine, just do it in a new process.  Much depends on this assumption - specifically the use of globals with functional programming over singletons with OOP.

## Functional Programming

Generally, a functional programming style is used.  Globals are ok, but don't overdo it.  Classes and objects are also ok, but don't overdo it.  Store things in standard collections if possible.

## API-minimal

Keep the API small, idiot-proof, transparent, and simple.  KISS the API.

Most things should be callable from "pyke".  e.g. "import pyke; pyke.add_target(...)".

Anything that is non-standard should have an explanation with it, and good justification for its existence.

## OS Agnostic-ish

The goal of pyke is to be mostly OS agnostic.  Linux and windows, specifically, are supported.  So all paths should be joined using os.path.join and any file structure manipulation should happen using python's os-agnostic libraries.  However, some linux-like standards are used, and development of pyke is supported primarily for linux.

## This is not a thing-that-does-everything-for-the-user

Part of impetus behind pyke is that other build architectures do too much for you, obscuring what actually happens, and increasing learning curve.  Pyke is intentionally small and transparent.  Conventions, conveyed through examples, will show best practices on how to set up the most common build tasks.

# Concepts

## Targets, Dependencies, Products, Conditions

Targets are the workhorse of pyke.  They are similar in concept to targets in both make and cmake.  Targets have dependencies, which must be valid before the target can run.  They also have an action and produce products.  When a target is requested to run, all of its dependencies, its dependencies' dependencies, etc. are run first, if need be.

Dependencies and products are lists of "Conditions".  A Condition can be in one of 3 states: invalid, valid, and updated.  A target cannot run until all of its dependencies are either valid or updated.  If a product is invalid, its target can satisfy its condition, at which point it becomes updated.  If a product is valid, a target can run and either mark it as updated if changes are made, or leave it as valid.  If all of a target's dependencies and products are valid, then the target will not need to run unless specified in other ways.

For example: the most common Condition is a FileCondition.  A FileCondition is valid if the file it is associated with has not changed since it was last updated.  If its file has been modified, then the file is invalid.  When the target runs that has the file as a product, it will mark the file as updated.  This is true for both things like source files and built files.

A Target's action is a callable object.  Popular actions include "copy files", "do nothing", and "compile something", but it could be nearly anything.

Conditions also have great flexibility.  Conditions have a "validate" function which could, say, check if a library is installed, or that a database is setup a certain way, or that a file has not been changed.  The validate function returns "valid" or "invalid"

Some Conditions need to keep some state to run validate.  State can only be kept around after the configuration stage.  See the next section for more on this.

Targets that don't have products are allowed, but since there is no way to tell if they need to be run, they will be always be run if selected.

## Stages and Configuration

A stage is a collection of targets.  Their intent is to produce a logical flow of dependencies where one stage cannot run until the entirety of the previous stages are complete.  Once a stage is complete, its products will not be checked again unless a target from that stage or earlier is requested.

One may define a default stage to which targets will be assigned unless otherwise specified.

The Config stage is a special stage that denotes the existence of a directory in which pyke can store its cache.  Prior to this stage, pyke must run statelessly.  Specifically FileConditions are not allowed because they require storing the state of the last time a file was modified.  The user can also store state from one run to another after configuration.  It is recommended that all data needed to build or enact later stages be gathered in the config stage and not modified after that.

# "Do We Support It?" Decisions

## Using ~ in paths: YES

All paths from the user should be passed through os.path.expanduser.

## Using environment variables in paths: NO

We will not be passing things through os.path.expandvar

## symbolic links basically everywhere: YES

This usually isn't a problem, but we may want to check that mtime (or whatever metric we're using) works on all the OSs the way we want it to.

## having both <path>/<name>/Pykefile and <path>/<name>.pyke: NO

This is a name colision and we basically consider them to be the same file.

## pyke.load skipping a directory: YES

From <path>/Pykefile you can call pyke.load('a/b') to load <path>/a/b/Pykefile.  This can be important in some situations where having a Pykefile in a directory can kind of mess things up.

## pyke.load from a ".pyke" file: YES

From <path>/<name>.pyke you can call pyke.load('A') which will do a "sibling-style load", loading either <path>/A/Pykefile or <path>/A.pyke.

## Changing the stages after pyke.init: NO

We see this as pretty static, so there shouldn't be a reason to change the stages.  Time will test this assumption.

## Accessing pykefiles via import statements: NO (basically)

Technically, because we are adding the pykefiles to sys.modules under "pyke.root", you CAN import them like `import pyke.root.blah as blah`  However, to access them like `import pyke; pyke.root.blah` requires having root be in the globals of pyke and blah be in the globals of root, which we are not willing to either require or enforce.

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

## Use "#!/bin/env python"

At the top of each python file, use the sh-bang line "#!/bin/env python".  This should allow the most IDEs to view the file correctly while remaining as python-environment-agnostic as possible.

## Use ' over "

Python doesn't have much distinction between single- and double-quotes.  Save yourself a shift-key and use single quotes.

## Default values occur in one place

Never define a default value for something in more than one place.  Therin lies madness.  Also, define the value as publicly as possible.  Meaning: if the default value affects the public API, put it in the public API.  If it affects public functions, put it in the public functions and not the private functions.

## Throw PykeException when things are not correct

The users are assumed to know some amount of python, they can handle a python traceback.  Put relavent info in the exception message including what general rule was broken and what the user passed in to make things not work.  It is ok for exception messages to be a bit long.

## Keep the number of exceptions small and all inherit from PykeException

We only need a few types of exceptions - noneed to reinvent existing exceptions.  All new exceptions should inherit from PykeException so the user can filter them out if they want.  Exceptions should be used for when something is not correct - we probably don't need to catch it, and it will likely end in halting program execution.

## Variable naming conventions for variables with files vs dirs, file/dir names vs paths, and relative vs absolute paths

From a variable name, we should know if a string represents a file, directory, or either; a path to the file/dir or just its name (basename, as in os.path.basename); and whether it is a relative or absolute path.

File and directory *names* should contain only the basename to that file/dir and not a path to it.  It should have "name" or be super obvious in the variable name.

Use absolute paths wherever possible.

Relative paths should include "rel" in the variable name.  Absolute paths are the default.

Directories should have "dir" in the variable name.  Files may have either "file or path" in the variable name (unless it is terribly obvious).

Do not create classes to distinguish these.  We are using conventions for this.

examples:
pykefile_path: an absolute path to a pykefile file
blah_reldir: a relative path to a directory related to "blah"
foo_dirname: the basename of the directory for "foo"
bar_dir: the absolute path to the directory for "bar"








