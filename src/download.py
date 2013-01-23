#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# AUTHOR:   xgfone
# DATE:     2013-1-22
# VERSION:  0.2
# PLATFORM: ALL
# EMAIL:    xgfone@126.com
# FUNCTION:
#           Download what you want through the multiprocessing or the multithreading.
# UPDATES:
#           (1) Adjust the watch.
#           (2) Add the watch with more than one file.
#           (3) Add the functions "is_default_tasks_information", "install_get_tasks_info",
#               "get_tasks_info", "install_downloader", "download_with_watch".
#           (4) Adjust the interface between the components, especially the form of the 
#               information that the downloader downloads the file.
#           (5) Adjust the downloader engine in order to permit the users use their 
#               downloader, only if they observe the interface between the downloader
#               and the downloader engine.
#           (6) Increase the thread-safe of the multithreading downloader.
#           (7) Correct, adjust and add other codes.
#
# LECENSE: 
# Copyright (c) 2012 xgfone
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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

_download_return_info = ["Can't open the URL: {}",
                         'Cannot download with breakpoint transmission, and you may have a try to set the\nargument "breakpoint" to False',
                         'Save the content of the URL without multithreading and breakpoint transmission',
                         'Download the file with breakpoint transmission and the multithreading']


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
                if r == 3:
                    print(analyse_result(get_tasks_info(filename), filename), end="\n\n")
                    continue

                print("================================================================================")
                if r == 0:
                    print(_download_return_info[r].format(url))
                    print("================================================================================\n")
                elif r == 1:
                    print(_download_return_info[r])
                    print("================================================================================\n")
                elif r == 2:
                    print(_download_return_info[r])
                    print("================================================================================")
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
    print("")
    print("Usage:")
    print("      {} [-dhnv][-D dir][-N number][-b breakpoint] [URL] [filename]\n".format(program_name))
    print("-h")
    print("    Print the help information\n")
    print("-n")
    print("    Without condition, close BREAKPOINT TRANSMISSION\n")
    print("-v")
    print("    Print the information of the copyright.\n")
    print("-b breakpoint")
    print("    Continue to breakpoint Transmission. Breakpoint information reads from the file \"breakpoint\"\n")
    print("-d directory")
    print("    the directory to save the downloading file\n")
    print("-N number")
    print("    Download the file by number threads or processes\n")
    print("URL")
    print("    the address where you will download what you want\n")
    print("filename")
    print("    the name of the file used to save what you will download\n")
    sys.exit(os.EX_OK)

if __name__ == "__main__":
    import getopt
    import pickle
    import http.client
    from urllib import error
    
    url = ""
    filename = ""
    tasks = task_number

    # Read the options of the command line.
    try:
        options, args = getopt.getopt(sys.argv[1:], "nhvd:N:b:")
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
                print("{0} does not exist!".format(val))
                sys.exit(os.EX_OK)
        elif "-n" == opt:
            pass
        elif "-v" == opt:
            print(os.path.split(sys.argv[0])[1], _version)
            print("Copyright (C) 2012 xgfone")
            sys.exit(os.EX_OK)
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
        print("The URL can not be empty.")
        sys.exit(os.EX_OK)
    url = handle_urls(url)
    filename = handle_filenames(filename, url)
    if os.path.lexists(filename[0]):
        y_or_n = input("{} has existed. Do you download it again? (y or n) ".format(filename[0]))
        while y_or_n not in ('y', 'Y', 'N', 'n'):
            y_or_n = input("Please input (y or n): ")
        if y_or_n in ('n', 'N'):
            print("Exit ...\n")
            sys.exit(os.EX_OK)

    try:
        download_with_watch(url, filename, breakpoint=False)
    except (SystemExit, KeyboardInterrupt):
        print("Exit ...")
        #with open(breakpoint_file, 'wb') as f:
        #    sorted(tasks_info().items(), key=lambda i: i[0])
        #    pickle.dump(tasks_info, f)
        

