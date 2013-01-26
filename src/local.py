# Copyright (C) xgfone 2013
# -*- coding: utf-8 -*-

import gettext
import locale
import os

_lang = locale.getdefaultlocale()[0]
_parent_dir = os.path.dirname(os.path.dirname(__file__))
_locale_dir = os.path.join(_parent_dir, 'local')

def install_gettext(domain, localedir=_locale_dir, languages=[_lang], fallback=True):
    _local = gettext.translation(domain, localedir, languages, fallback=fallback)
    _local.install()
    
