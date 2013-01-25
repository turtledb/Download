# Copyright (C) xgfone 2013
# -*- coding: utf-8 -*-

import gettext
import locale

_lang = locale.getdefaultlocale()[0]

def install_gettext(domain, localedir='../local', languages=[_lang], fallback=True):
    _local = gettext.translation(domain, localedir, languages, fallback=fallback)
    _local.install()
    
