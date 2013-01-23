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

#try:
#    from _thread import interrupt_main
#except ImportError:
#    from _dummy_thread import interrupt_main

__all__ = ["thread_download", "get_tasks_info"]
_tasks_information = {}

def get_tasks_info(filenames=None):
    """
    Return a dict representing the information of downloading tasks.
    The key is the name of the file you want to download, and the value is the information
    about this file. The value is a list containing five elements: the first element is 
    bool, and True representing it uses the multithreading, and False not; the second is
    a string, representing the URL where this file locates; the third is a integer, 
    representing the total time(second) to download this file; the fourth is also a integer,
    representing the total size(Byte) of this file if the first is True, otherwise the size(Byte)
    you have downloaded. The fifth is a dict, representing the information of all the threads;
    and the key is a the name of the thread, and the value is a list, that is, [temp_filename,
    start_position, end_position, length, downloaded_size, etag, last_modified]. Thereinto,
    "temp_filename" is the name of the file used to save temporarily what you have downloaded;
    and "length" == "end_position" - "start_position" + 1. But if the first element is False, the
    fifth is None.

    For example:
    {"/home/user/Download/example1.mp4": [True, "http://www.example.com/example1.mp4", 0, 12345678,
                                         {"thread_1": [0, 9999999, 10000000, 10000000, None, None, "/tmp/example1_01.mp4"],
                                          "thread_2": [10000000, 12345677, 2345678, 2000000, None, None, "/tmp/example1_02.mp4"]
                                         }],
     "/home/user/Download/example2.mp4": [True, "http://www.example.com/example2.mp4", 0, 87654321,
                                         {"thread_1": [0, 79999999, 80000000, 80000000, None, None, "/tmp/example2_01.mp4"],
                                          "thread_2": [80000000, 87654320, 87654321, 7000000, None, None, "/tmp/example2_02.mp4"]
                                         }]
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

    
################################# Private Information ##################################
# the byte number of the file which every thread will download
# If exceeding it, download cyclically. Default is 10M.
_bytes_per_time = 10485760

_thread_number = 10  # the number of the thread used to download the file
_max_thread_number = 20       # the maximal number of the thread or the process permited
_bytes_reading_from_buffer = 8192    # The default is 8K charactors, not 8K Bytes.
_thread_lock = RLock()        # the lock used to visit the global variable among threads
_retry_number = 3
######################################## END ###########################################

class ThreadDownloadTask(Thread):
    """
    The downloader to download the file,  whose implementation is using the thread.
    """
    def __init__(self, url, file, filename, start=None, end=None, thread_name=None,
                 etag=None, last_modified=None):
        """
        Download [start, end] in the "url" into "file".
        If "start" or "end" is None, download the file through the breakpoint transmission; 
        Or, not the breakpoint transmission.
        """
        Thread.__init__(self, name=thread_name)
        self.url = url
        self.file = file
        self.filename = filename
        self.etag = etag
        self.last_modified = last_modified
        self.startpos = start
        self.endpos = end

        _thread_lock.acquire()
        if _tasks_information[filename][4] is not None:
            breakpoint = True
        else:
            breakpoint = False
        _thread_lock.release()
        
        if breakpoint:
            self.length = self.endpos - self.startpos + 1   # the length of the downloading file
            
            # split [start, end] into multi-section to download from a section to another.
            self.request_ranges = [self.startpos]
            if self.length > _bytes_per_time:
                tmp = self.length
                while tmp > _bytes_per_time:
                    self.request_ranges.append(self.request_ranges[-1] + _bytes_per_time)
                    tmp -= _bytes_per_time
                self.request_ranges.append(self.endpos)
            else:
                self.request_ranges.append(self.endpos)
        else:
            self.length   = None
            self.request_ranges = None
        
        self.retry_number = _retry_number
        self.request = Request(url = self.url)

    def download(self, start=None, end=None):
        """
        Doanload from "start" to "end" really.
        If "start" or "end" is None, download the file through the breakpoint transmission; 
        Or, not the breakpoint transmission.
        """
        # not the breakpoint transmission
        if start is None or end is None:
            # If Request failed, retry it, but most self.retry_number times.
            while self.retry_number:
                try:
                    connect = urlopen(self.request)
                except urllib.error.URLError:
                    self.retry_number -= 1
                else:
                    if connect is None:
                        return
                    break
            if not self.retry_number:
                return

            #self.file.write(connect.read())
            #self.file.flush()
            #connect.close()
            #_thread_lock.acquire()
            #_tasks_information[self.filename][3] = self.file.tell()
            #_thread_lock.release()
            d = connect.read(_bytes_reading_from_buffer)
            while d:
                self.file.write(d)
                self.file.flush()
                _thread_lock.acquire()
                _tasks_information[self.filename][3] = self.file.tell()
                _thread_lock.release()
                d = connect.read(_bytes_reading_from_buffer)
            connect.close()
            return

        # set the HEADER to use the breakpoint transmission.
        self.request.add_header("Range", "bytes={:d}-{:d}".format(start, end))
        if self.etag:
            self.request.add_header("If-Range", self.etag)
        if self.last_modified:
            self.request.add_header("Unless-Modified-Since", self.last_modified)

        # If Request failed, retry it, but most self.retry_number times.
        while self.retry_number:
            try:
                connect = urlopen(self.request)
            except urllib.error.URLError:
                self.retry_number -= 1
            else:
                if connect is None:
                    return
                break
        if not self.retry_number:
            return

        #self.file.write(connect.read())
        #self.file.flush()
        #connect.close()
        #_thread_lock.acquire()
        #_tasks_information[self.filename][4][self.name][4] = self.file.tell()
        #_thread_lock.release()
        d = connect.read(_bytes_reading_from_buffer)
        while d:
            self.file.write(d)
            self.file.flush()
            _thread_lock.acquire()
            _tasks_information[self.filename][4][self.name][4] = self.file.tell()
            _thread_lock.release()
            d = connect.read(_bytes_reading_from_buffer)
        connect.close()

    def run(self):
        # Save the information of the breakpoint transmission into the global variable.
        _thread_lock.acquire()
        if _tasks_information[self.filename][4] is not None:
            breakpoint = True
        else:
            breakpoint = False
        _thread_lock.release()

        # breakpoint transmission
        if breakpoint:
            _tasks_information[self.filename][4][self.name] = [self.file.name, self.startpos, self.endpos, self.length,
                                                               self.file.tell(), self.etag, self.last_modified]
            if self.startpos > self.endpos:
                return
            # download cycliclally.
            for i in range(len(self.request_ranges) - 2):
                self.download(self.request_ranges[i], self.request_ranges[i+1] - 1)
            self.download(self.request_ranges[-2], self.request_ranges[-1])
        else:    # not breakpoint transmission
            self.download()
                

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
    retry_number = _retry_number
    while retry_number:
        try:
            connect = urlopen(url)
        except urllib.error.URLError:
            retry_number -= 1
        else:
            if connect is None:
                return 0
            break
        
    if not retry_number:
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
    _tasks_information[filename] = [None, url, 0, 0, {}]
    _thread_lock.release()

    # The server doesn't support the breadpoint transmission, and download it
    # at a time.
    if not accept_ranges or not length:
        _thread_lock.acquire()
        _tasks_information[filename][0] = False
        _tasks_information[filename][4] = None
        _thread_lock.release()
        file = open(filename, "wb")
        task = ThreadDownloadTask(url, file, filename, None, None, '0', etag, last_modified)
        start_time = time.time()
        task.start()
        task.join()
        end_time = time.time()
        file.close()
        _thread_lock.acquire()
        _tasks_information[filename][2] = int(end_time - start_time)
        _thread_lock.release()
        return 2

    _thread_lock.acquire()
    _tasks_information[filename][0] = True
    _tasks_information[filename][3] = length
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
        task = ThreadDownloadTask(url, file, filename, ranges[i], ranges[i+1] - 1, str(i+1), etag, last_modified)
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
        
        d = f.read(_bytes_reading_from_buffer)
        while d:
            out_file.write(d)
            out_file.flush()
            d = f.read(_bytes_reading_from_buffer)
        f.close()
        os.remove(f.name)
    out_file.close()

    return 3


