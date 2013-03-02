# Copyright (c) xgfone 2012-2013
# -*- coding: utf-8 -*-

import os
import time
import copy
import urllib.error
from urllib.request import Request, urlopen
try:
    from threading import Thread, RLock
except ImportError:
    from dummy_threading import Thread, RLock

__all__ = ["thread_download", "get_tasks_info"]
_tasks_information = {}

################################# Private Information ##################################
# the byte number of the file which every thread will download
# If exceeding it, download cyclically. Default is 10M.
_bytes_per_time = 8192 #10485760

_thread_number = 10  # the number of the thread used to download the file
_max_thread_number = 20       # the maximal number of the thread or the process permited
_thread_lock = RLock()        # the lock used to visit the global variable among threads
######################################## END ###########################################

def get_tasks_info(filenames=None):
    """
    Return a dict representing the information of downloading tasks.
    The key is the name of the file you want to download, and the value is the information
    about this file. The value is a list containing six elements: the first element is 
    bool, and True representing it uses the multithreading, and False not; the second is
    a string, representing the URL where this file locates; the third is a integer, 
    representing the total time(second) to download this file; the fourth is also a integer,
    representing the total size(Byte) of this file if the first is True, otherwise the size(Byte)
    you have downloaded. The fifth is a dict, representing the information of all the threads;
    and the key is a the name of the thread, and the value is a list, that is, [temp_filename,
    start_position, end_position, length, downloaded_size]. Thereinto, "temp_filename" is the
    name of the file used to save temporarily what you have downloaded; and "length" == 
    "end_position" - "start_position" + 1. But if the first element is False, the fifth is None.
    And the sixth is the etag of the file, and the last is the last modified datetime of that.
    For example:
    {"/home/user/Download/example1.mp4": [True, "http://www.example.com/example1.mp4", 0, 12345678,
                                         {"thread_1": ["/tmp/example1_01.mp4", 0, 9999999, 10000000, 10000000],
                                          "thread_2": ["/tmp/example1_02.mp4", 10000000, 12345677, 2345678, 2000000]
                                         }, None, None],
     "/home/user/Download/example2.mp4": [True, "http://www.example.com/example2.mp4", 0, 87654321,
                                         {"thread_1": ["/tmp/example2_01.mp4", 0, 79999999, 80000000, 80000000],
                                          "thread_2": ["/tmp/example2_02.mp4", 80000000, 87654320, 87654321, 7000000]
                                         }, None, None]
    }
    """
    rtn = {}
    _thread_lock.acquire()
    if filenames is None:
        rtn = copy.deepcopy(_tasks_information)
    elif not isinstance(filenames, (list, tuple)):
        try:
            rtn = {filenames: copy.deepcopy(_tasks_information[filenames])}
        except KeyError:
            pass
    else:
        for f in filenames:
            try:
                rtn[f] = copy.deepcopy(_tasks_information[f])
            except KeyError:
                pass
    _thread_lock.release()
    return rtn
                
def _retry_connect(url, number=3):
    while number > 0:
        try:
            connect = urlopen(url)
        except urllib.error.URLError:
            number -= 1
        else:
            if connect is None:
                return None
            return connect
    return None

class _ThreadDownloadTask(Thread):
    """
    The downloader to download the file,  whose implementation is using the thread.
    """
    def __init__(self, url, file, filename, start=None, end=None, thread_name=None):
        """
        Download [start, end] in the "url" into "file".
        If "start" or "end" is None, download the file through the breakpoint transmission;
        Or, not the breakpoint transmission.
        """
        Thread.__init__(self, name=thread_name)
        self.url = url
        self.file = file
        self.filename = filename
        self.startpos = start
        self.endpos = end
        self.request = Request(url = self.url)

        if start is not None and end is not None:
            self.length = self.endpos - self.startpos + 1
        else:
            self.length   = None

    def run(self):
        """
        Request the URL with the breakpoint transmission or not. If using the 
        breakpoint transmission, add the information of the breakpoint
        transimission; or, nothing, that is, request the URL directly.
        """
        # breakpoint transmission
        if self.length:
            _thread_lock.acquire()
            _tasks_information[self.filename][4][self.name] = [self.file.name, self.startpos, self.endpos, self.length, self.file.tell(), False]
            _thread_lock.release()

            if self.startpos > self.endpos:
                return

            self.request.add_header("Range", "bytes={:d}-{:d}".format(self.startpos, self.endpos))
        
        connect = _retry_connect(self.request)
        if connect is None:
            return
        
        content = connect.read(_bytes_per_time)
        while content:
            self.file.write(content)
            self.file.flush()
            _thread_lock.acquire()
            if self.length:
                _tasks_information[self.filename][4][self.name][4] = self.file.tell()
            else:
                _tasks_information[self.filename][3] = self.file.tell()
            _thread_lock.release()
            content = connect.read(_bytes_per_time)
        connect.close()
        
def _not_breakpoint_download(url, filename):
    _thread_lock.acquire()
    _tasks_information[filename][0] = False
    _tasks_information[filename][4] = None
    _thread_lock.release()
    file = open(filename, "wb")
    task = _ThreadDownloadTask(url, file, filename, thread_name='0')
    start_time = time.time()
    task.start()
    task.join()
    end_time = time.time()
    file.close()
    _thread_lock.acquire()
    _tasks_information[filename][2] = int(end_time - start_time)
    _thread_lock.release()

def _breakpoint_download(url, filename, temp_dir, number, length):
    _thread_lock.acquire()
    _tasks_information[filename][0] = True
    _thread_lock.release() 

    # Allocate the downloads for every thread.
    if length  <= 1048576:    # 1M == 1048576
        number = 1
    if number > _max_thread_number:
        number = _max_thread_number
    size_per_thread = length // number
    ranges = [0]
    for i in range(number - 1):
        ranges.append((i + 1) * size_per_thread)
    ranges.append(length)
    
    # Create the threads to download it group by group.
    files = []
    tasks = []
    tmp_filename = os.path.join(temp_dir, os.path.split(filename)[1])
    for i in range(len(ranges) - 1):
        file = open("{}_parted{:02d}".format(tmp_filename, i), "wb+")
        files.append(file)
        task = _ThreadDownloadTask(url, file, filename, ranges[i], ranges[i+1] - 1, str(i+1))
        tasks.append(task)

    start_time = time.time()
    # Start all the threads.
    for t in tasks:
        t.start()

    # Stop the main thread until all the threads are not alive.
    for t in tasks:
        t.join()

    end_time = time.time()
    _thread_lock.acquire()
    _tasks_information[filename][2] = int(end_time - start_time)
    _thread_lock.release()

    # So far, all the threads have downloaded the files.
    # So Merge those files into one whole file.
    out_file = open(filename, "wb")
    for f in files:
        f.seek(0)
        
        d = f.read(_bytes_per_time)
        while d:
            out_file.write(d)
            out_file.flush()
            d = f.read(_bytes_per_time)
        f.close()
        os.remove(f.name)
    out_file.close()


def thread_download(url, filename, temp_dir, number=_thread_number, breakpoint=True):
    """
    Use "number" "downloader"s to download "filename" from "url".
    @filename:   the name of the file to save what you will download
    @number:     the number of "downloader"
    @

    RETURN:
           0 -- Can't open the URL
           1 -- must use breakpoint transmission, but that website doesn't support it.
           2 -- that website doesn't support breakpoint transmission, so use save the
                URL without the multithreading. 
           3 -- that website spport breakpoint transmission, and use the multithreading
                to download the file.
    """
 
    # Check whether the server supports the breakpoint transmission, and get the 
    # length of the downloading file, in order to download group by group.
    connect = _retry_connect(url)
    if connect is None:
        return 0

    accept_ranges = connect.headers.get("Accept-Ranges")
    length = int(connect.headers.get("Content-Length", 0))
    etag = connect.headers.get("ETag")
    last_modified = connect.headers.get("Last-Modified")
    connect.close()

    # If must use breakpoint transmission, but website doesn't support it.
    if breakpoint and (not accept_ranges or not length):
        return 1

    _thread_lock.acquire()
    _tasks_information[filename] = [None, url, 0, length, {}, etag, last_modified]
    _thread_lock.release()

    if not accept_ranges or not length:
        _not_breakpoint_download()
        return 2
    else:
        _breakpoint_download(url, filename, temp_dir, number, length)
        return 3

