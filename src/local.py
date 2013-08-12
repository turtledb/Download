# Copyright (C) xgfone 2013
# -*- coding: utf-8 -*-

import gettext
import locale
import os
import py3or2

_lang = locale.getdefaultlocale()[0]
_parent_dir = os.path.dirname(os.path.dirname(__file__))
_locale_dir = os.path.join(_parent_dir, 'local')

def install_gettext(domain, localedir=_locale_dir, languages=[_lang], fallback=True, windows=False):
    if os.name != "posix" or os.name != "mac" or not windows:
        if py3or2.PY3:
            import builtins
        else:
            import __builtin__ as builtins
        builtins._ = lambda v: v
    else:
        _local = gettext.translation(domain, localedir, languages, fallback=fallback)
        _local.install()

