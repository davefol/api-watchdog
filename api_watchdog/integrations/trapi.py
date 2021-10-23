from types import SimpleNamespace

try:
    from reasoner_pydantic import *
except ImportError:
    reasoner_pydantic = SimpleNamespace()
        #raise NotImplementedError("Must install with 'TRAPI' extension")

def istrapi(x):
    module = getattr(x, '__module__', None)
    if type(module) is str:
        return module.startswith("reasoner_pydantic")
    else:
        return False

