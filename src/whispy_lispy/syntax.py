import six

if six.PY2:
    str = unicode


class LispySyntaxError(Exception):
    pass