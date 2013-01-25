#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# FUNCTION: Download what you want through the multiprocessing or the multithreading.
# NOTICES:  If the downloaded percent is over 100%, it indicates the URL of the file
#           you want to download has changed. Please download it again.
#

import re
import os
import sys
import time
import shutil
import watch
import result_analyse
import downloader_handle
from urllib.parse import urlparse
try:
    from threading import Thread
except ImportError:
    from dummy_threading import Thread

__all__ = ["install_downloader", "is_default_tasks_information", "install_get_tasks_info",
           "get_tasks_info", "watch", "watch_files", "handle_filenames", "handle_urls",
           "download", "download_with_watch", "analyse_result", "result", "format_time",         
           "format_bytes"]

install_downloader = downloader_handle.install_downloader
is_default_tasks_information = downloader_handle.is_default_tasks_information
install_get_tasks_info = downloader_handle.install_get_tasks_info
get_tasks_info = downloader_handle.get_tasks_info

watch_files = watch.watch_files
watch  = watch.watch

analyse_result = result_analyse.analyse_result
result = result_analyse.result
format_bytes = result_analyse.format_bytes
format_time  = result_analyse.format_time


debug = False
task_number = 10
breakpoint_file = "breakpoint_transmission.info"
directory_to_save_file = '~/Download'
temp_directory_to_save_file = os.path.join(directory_to_save_file, "_TEMP_")

def _handle_url(url):
    """
    Get the URL of the downloading file, and check its validity, that is, it must
    begin with "http://". If not, add "http://" at the beginning of URL.
    """
    if not url:
        return None
    if not re.match("[hH][tT][tT][pP][sS]?://.+", url):
        url = ''.join(('http://', url.lstrip(' \t\n')))
    return url

def handle_urls(urls):
    if not isinstance(urls, (list, tuple)):
        return [_handle_url(urls)]
    else:
        rtn = []
        for u in urls:
            rtn.append(_handle_url(u))
        return rtn

def _handle_filename(filename, url=None):
    """
    Get the filename used to save the downloading file, which includes the path.
    The filename must conform with the local OS. In addition, check whether the
    filename is validity.
    """
    if not filename and not url:
        return None
    if not filename and url:
        url_split = urlparse(url)
        name = os.path.split(url_split.path)
        filename =  name[1] if name[1] else url_split.netloc
    rtn = os.path.split(filename)
    if not rtn[0]:
        filename = os.path.join(directory_to_save_file, filename)
    else:
        try:
            os.makedirs(rtn[0])
        except OSError:
            pass
    filename = os.path.expanduser(filename)
    filename = os.path.abspath(filename)
    return filename

def handle_filenames(filenames, urls=None):
    if not isinstance(filenames, (list, tuple)):
        if urls:
            if isinstance(urls, (list, tuple)):
                return [_handle_filename(filenames, urls[0])]
        return [_handle_filename(filenames, urls)]
    else:
        rtn = []
        if urls and isinstance(urls, (list, tuple)):
            for f, u in zip(filenames, urls):
                rtn.append(_handle_filename(f, u))
            return rtn

        for f in filenames:
            rtn.append(_handle_filename(f, urls))
        return rtn

def download(urls, filenames, temp_dir=temp_directory_to_save_file, task_number=task_number,
             breakpoint=True, result=True, downloader=None, get_task_info=None):
    temp_dir = os.path.abspath(os.path.expanduser(temp_dir))
    try:
        os.makedirs(temp_dir)
    except OSError:
        pass
    urls = handle_urls(urls)
    filenames = handle_filenames(filenames, urls)
    
    if downloader is not None:
        install_downloader(downloader)
    if get_task_info is not None:
        install_get_tasks_info(get_task_info)

    # Start the download.
    rtn = []
    for url, filename in zip(urls, filenames):
        if url and filename:
            name = os.path.split(filename)[1]
            loc = name.rfind('.')
            if loc == -1:
                temp_subdir = os.path.join(temp_dir, name)
            else:
                temp_subdir = os.path.join(temp_dir, name[:loc])
            try:
                os.makedirs(temp_subdir)
            except OSError:
                pass

            r = downloader_handle._real_downloader(url, filename, temp_subdir, task_number, breakpoint)
            shutil.rmtree(temp_subdir, True)

            rtn.append((url, filename, r))
            if result:
                if r == 0:
                    print("================================================================================")
                    print(_("Can't open the URL: {}").format(url))
                    print("================================================================================\n")
                elif r == 1:
                    print("================================================================================")
                    print(_('Cannot download with breakpoint transmission, and you may have a try to set the\nargument "breakpoint" to False'))
                    print("================================================================================\n")
                elif r == 2:
                    print("================================================================================")
                    print(_('Save the content of the URL without multithreading or multiproccess'))
                    print("================================================================================")
                    print(analyse_result(get_tasks_info(filename), filename), end="\n\n")
                elif r == 3:
                    print(analyse_result(get_tasks_info(filename), filename), end="\n\n")
    return rtn
            
def download_with_watch(urls, filenames, temp_dir=temp_directory_to_save_file, task_number=task_number, 
                        breakpoint=True, result=True, downloader=None, get_task_info=None):
    if downloader is not None:
        install_downloader(downloader)
    if get_task_info is not None:
        install_get_tasks_info(get_task_info)
    
    if not isinstance(urls, (list, tuple)) or not isinstance(filenames, (list, tuple)):
        task = Thread(target=download, args=(urls, filenames, temp_dir, task_number, breakpoint, result))
        task.start()
        watch(filename, task)
        return

    for (url, filename) in zip(urls, filenames):
        task = Thread(target=download, args=(url, filename, temp_dir, task_number, breakpoint, result))
        task.start()
        watch(filename, task)
    return

# Install the default downloader and the default get_tasks_info
install_downloader()
install_get_tasks_info()
            
def _usage(program_name):
    """
    Print the usage of the program.
    @program_name:  the name of this program
    """
    print("Copyright (C) 2012 - 2013, xgfone")
    print(_("Usage:"))
    print("      {} [-dhn][-D dir][-N number][-b breakpoint] [URL] [filename]".format(program_name))
    print(_("      Download what you want through the multiprocessing or the multithreading."), end='\n\n')
    print("-h")
    print(_("    Print the help information"), end='\n\n')
    print("-n")
    print(_("    Without condition, don't continue the last uncompleted task"), end='\n\n')
    print("-b breakpoint")
    print(_("    Continue the last uncompleted task"), end='\n\n')
    print("-d directory")
    print(_("    the directory to save the downloading file"), end='\n\n')
    print("-N number")
    print(_("    Download the file by number threads or processes"), end='\n\n')
    print("URL")
    print(_("    the address where you will download what you want"), end='\n\n')
    print("filename")
    print(_("    the name of the file used to save what you will download"), end='\n\n')
    sys.exit(os.EX_OK)

if __name__ == "__main__":
    import getopt
    import pickle
    import local
    import locale
    import http.client
    from urllib import error
    locale.setlocale(locale.LC_ALL, '')
    local.install_gettext("messages")

    url = ""
    filename = ""
    tasks = task_number

    # Read the options of the command line.
    try:
        options, args = getopt.getopt(sys.argv[1:], "nhd:N:b:")
    except getopt.GetoptError:
        usage(os.path.split(sys.argv[0])[1])
    _breakpoint = False
    for opt, val in options:
        if "-N" == opt:
            val = int(val)
            if val > 0:
                tasks = val
        elif "-b" == opt:
            breakpoint_file = val
            _breakpoint = True
        elif "-d" == opt:
            if os.path.lexists(val):
                directory_to_save_file = val
            else:
                print(_("{0} does not exist!").format(val))
                sys.exit(os.EX_OK)
        elif "-n" == opt:
            pass
        else:
            _usage(os.path.split(sys.argv[0])[1])
    for opt, val in options:
        if "-n" == opt:
            breakpoint_file = None
            break

    # If the breakpoint transmission file exists, ignore the original download, 
    # and continue the last breakpoint transmission.
    #if breakpoint_file is not None and os.access(breakpoint_file, os.F_OK | os.R_OK):
    #    rtn = {}
    #    with open(breakpoint_file, 'rb') as f:
    #        rtn = pickle.load(f)
    #    try:
    #        from breakpoint_recover import recover_breakpoint_download
    #    except ImportError:
    #        pass
    #    else:
    #        recover_breakpoint_download(rtn)
    #        sys.exit(os.EX_OK)
    #if _breakpoint:
    #    print("The breakpoint transmission file does not exist; or you has no permission to read it.")
    #    sys.exit(os.EX_OK)

    length = len(args)
    if length > 0:
        url = args[0]
    if length > 1:
        filename = args[1]
    if not url:
        print(_("The URL can not be empty."))
        sys.exit(os.EX_OK)
    url = handle_urls(url)
    filename = handle_filenames(filename, url)
    if os.path.lexists(filename[0]):
        y_or_n = input(_("{} has existed. Do you download it again? (y or n) ").format(filename[0]))
        while y_or_n not in ('y', 'Y', 'N', 'n'):
            y_or_n = input(_("Please input (y or n): "))
        if y_or_n in ('n', 'N'):
            print(_("Exit ..."), end='\n\n')
            sys.exit(os.EX_OK)

    try:
        download_with_watch(url, filename, breakpoint=False)
    except (SystemExit, KeyboardInterrupt):
        print(_("Exit ..."))
        #with open(breakpoint_file, 'wb') as f:
        #    sorted(tasks_info().items(), key=lambda i: i[0])
        #    pickle.dump(tasks_info, f)
        

