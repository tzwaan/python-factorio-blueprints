import sys
from importlib import import_module


def _import(module, klass, clear=False):
    if clear:
        try:
            del sys.modules[module]
        except KeyError:
            pass
    module_object = import_module(module)
    return getattr(module_object, klass)
