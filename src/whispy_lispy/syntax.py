import six

if six.PY2:
    str = unicode

class SymbolMeta(type):
    def __instancecheck__(self, instance):
        if isinstance(instance, str):
            return True

class Symbol(object):
    __metaclass__ = SymbolMeta


class LispySyntaxError(Exception):
    pass