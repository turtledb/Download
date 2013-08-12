# Copyright (C) xgfone 2012 - 2013
# -*- coding: utf-8 -*-

import os

__all__ = ["install_downloader", "install_get_tasks_info", "get_tasks_info",
           "is_default_tasks_information"]

_real_downloader = None


def install_downloader(downloader=None):
    global _real_downloader
    if downloader is None:
        # Install the default downloader.
        if os.name == "posix" or os.name == "mac":
            # On POSIX, use the process. But now it don't be implemented, 
            # so here use still the thread.
            import thread_download as download
        else:
            # on Window.
            import thread_download as download
        _real_downloader = download.thread_download
    else:
        _real_downloader = downloader


def _tasks_information(filenames=None):
    return {}


_default_tasks_information = _tasks_information


def is_default_tasks_information():
    return _default_tasks_information == _tasks_information


def install_get_tasks_info(func=None):
    global _tasks_information
    if func is None:
        # Install the default get_tasks_info function.
        if os.name == "posix" or os.name == "mac":
            # On POSIX, use the process. But now it don't be implemented, 
            # so here use still the thread.
            import thread_download as download
        else:
            # on Window.
            import thread_download as download
        _tasks_information = download.get_tasks_info
    else:
        _tasks_information = func


def get_tasks_info(filenames=None):
    return _tasks_information(filenames)
    
    
