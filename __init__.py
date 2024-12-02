import importlib

__all__ = ['complicated']

def __getattr__(name):
  if name in __all__:
    return importlib.import_module("." + name, __name__)
  else:
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def __dir__():
  return __all__