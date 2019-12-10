===========
safetydance
===========


`safetydance` is a Python framework for defining type-safe and flexibly composable
application steps with a shared execution context for sharing variables between the
steps. The design of safetydance is partially inspired by `<https://cucumber.io>`_.


Description
===========

`safetydance` defines a set of decorators that rewrite functions as steps and scripts.

A step should be a function with a name that reads easily, like a short phrase or
sentence. Steps may take arguments and they may access variables defined for the
"context scope". Steps may call other steps, too.

A script is a function composing the execution of a series of steps. A script is a step
that defines an execution context. Scripts may also call other scripts. The primary
difference between a script and a step is the implicit definition of the execution
context. *TODO* When a script calls another script the current execution context *may*
be passed as a kwarg to the nested script; by default all scripts execute in their own
execution context; that is, if a step is used by both an originating and a nested script
the context variables it accesses are determined by the calling script's execution
context.

Context Scope Variables
-----------------------

A context scope variable is sort of like a global variable. The run of a script defines
a context where `context_data` variables are stored for access by steps.

Think of a conversation between two friends. Much of the conversation will reference
assumed shared knowledge, or context. For `safetydance`, the context scope provides a
way for steps to share assumed context to make it possible to provide a more
conversational style of programming

Future Work
===========

* Mypy extension to validate scripts. For example, prove that a script shouldn't fail
  due to missing `context_data` for any step in the script.
* Dry run execution of steps
* DAG derivation for scripts
* Parallel evaluation for independent up to a join for DAG legs of a script.
* Diagram output for script DAGs.

Setup for Development
=====================

Run `python setup.py develop`. Preferably, use `conda` or another virtual environment.

Note
====

This project has been set up using PyScaffold 3.2. For details and usage
information on PyScaffold see https://pyscaffold.org/.
