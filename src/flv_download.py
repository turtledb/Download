#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# AUTHOR:   xgfone
# DATE:     2013-1-22
# VERSION:  0.2
# PLATFORM: ALL
# EMAIL:    xgfone@126.com
#
# REQUIREMENT: 
#           (1)Python3 --- an interpreter programming language, >= 3.
#           (2)BeautifulSoup4 --- a python package, >= 4.
#           (3)download ---- a module, which downloads a file through the multiprocessing
#              or the multithreading.
#
# FUNCTION:
#           Download the flv video coming from www.youku.com, www.ku6.com, www.tudou.com,
#           v.qq.com, www.56.com, v.163.com, www.letv.com, www.cctv.com, v.ifeng.com,
#           www.m1905.com, video.sina.com.cn, www.kugou.com, kankan.xunlei.com(partial),
#           and so on, only if you give the URL of the file. 
#
#           In a word, only if the website(www.flvcd.com) can parse it, this program 
#           can download the file. Thank for www.flvcd.com.
#
# UPDATES:
#           (1) Adjust the codes according to the module "download".
#           (2) Change the old codes to a class "FLVCD".
#           (3) Define the interface parsing the URL from the third websits.
#           (4) Add the class "FLVXZ", parsing the URL from www.flvxz.com. But the website
#               may have a bit questiones, or the class is not perfect, so the class can't
#               work successfully.
#
# PROBLEM: 
#           (1) If it can't download what you want, please first check whether the URL 
#               which you gave is probably parsed by www.flvcd.com. If parsed, please
#               contact me; if not, it indicates that what you want can't be downloaded.
#           (2) The class "FLVXZ" can't work successfully. urllib.request.urlopen can't
#               acquire the whole result website. So it must use a especial way. I hope
#               someone to solve it. I will give the interface later.
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
import bs4
import time
import getopt
from urllib import error
from urllib.request import urlopen
from urllib.parse import urlparse
import download
try:
    from threading import Thread
except ImportError:
    from dummy_threading import Thread

directory_to_save_file = download.directory_to_save_file
temp_download_directory = download.temp_directory_to_save_file

def _check_others(basic_high_super, variety):
    index_ = (0, 1, 2)
    if variety == 0:
        print("There is not the basic video.")
    elif variety == 1:
        print("There is not the high video.")
    elif variety == 2:
        print("There is not the super video.")

    tmp_ = 0
    for i in index_:
        if basic_high_super[i]:
            tmp_ += 1

    if tmp_ == 0:
        if variety == 0:
            print("There are also not the high video and the super.")
        elif variety == 1:
            print("There are also not the basic video and the super.")
        else:
            print("There are also not the basic video and the high.")
    elif tmp_ == 1:
        for i in index_:
            if basic_high_super[i]:
                if i == 0:
                    print("There is the {} video, and you can use the -{} option.".format('basic', 'b'))
                elif i == 1:
                    print("There is the {} video, and you can use the -{} option.".format('high', 'H'))
                else:
                    print("There is the {} video, and you can use the -{} option.".format('super', 's'))
    elif tmp_ == 2:
        for i in index_:
            if basic_high_super[i]:
                if i == 0:
                    print("There is the {} video(the option: -{}), and ".format('basic', 'b'), end='')
                elif i == 1:
                    print("There is the {} video(the option: -{}), and ".format('high', 'H'), end='')
                else:
                    print("There is the {} video(the option: -{}), and ".format('super', 's'), end='')
                break
        for j in index_:
            if j != i and basic_high_super[j]:
                if j == 0:
                    print("the {} video(the option: -{}).".format('basic', 'b'))
                elif j == 1:
                    print("the {} video(the option: -{}).".format('high', 'H'))
                else:
                    print("the {} video(the option: -{}).".format('super', 's'))
    print()

class FLVCD:
    """
    Parse the URL from "www.flvcd.com".
    """
    def __init__(self, url, variety):
        self.url = url
        self.variety = variety
        self._request_variety = variety
        self._urls = []
        self._search_url = ['http://www.flvcd.com/parse.php?format=&kw=', # basic
                            'http://www.flvcd.com/parse.php?flag=one&format=high&kw=', # high
                            'http://www.flvcd.com/parse.php?flag=one&format=super&kw=', # super
                            ]

    def parse_url(self):
        try:
            con = urlopen(''.join((self._search_url[self._request_variety], self.url)))
            soup = bs4.BeautifulSoup(con.read())
            con.close()
            url_nodes = soup.body.find_all(class_= "mn STYLE4")
            url_a = url_nodes[2].find_all("a")
        except (error.URLError, IndexError):
            return None
        
        self._urls = []
        for u in url_a:
            href = u.get('href')
            if href and re.match('[Hh][Tt][Tt][Pp][Ss]?://', href):
                self._urls.append(href)
        return self._urls

    def check_others(self):
        basic_high_super = [False, False, False] 
        for i in (0, 1, 2):
            if self.variety != i:
                self._request_variety = i
                urls = self.parse_url()
                if urls:
                    basic_high_super[i] = True
        _check_others(basic_high_super, self.variety)

class FLVXZ:
    """
    Parse the URL from www.flvxz.com.
    """
    def __init__(self, url, variety):
        self.url = url
        self.variety = variety
        self._urls = [[], [], []]
        self._search_url = "http://www.flvxz.com/?url="
        self._re = re.compile("[超高标]清.*")
        
    def parse_url(self):
        try:
            con = urlopen(''.join((self._search_url, self.url)))
            soup = bs4.BeautifulSoup(con.read())
            con.close()
            url_nodes = soup.body.find(id="result")
            url_br = url_nodes.find_all("br")
        except (error.URLError, IndexError):
            return None

        current_kind = 0
        for br in url_br:
            if re.match(self._re, br.get_text()):
                prefix = br.get_text()[1:4]
                if prefix == "超清":
                    current_kind = 2
                elif prefix == "高清":
                    current_kind = 1
                elif prefix == "标清":
                    current_kind = 0
                else:
                    continue
            else:
                url = br.a.get('href')
                if url:
                    self._urls[current_kind].append(url)
                    
        return self._urls[self.variety]

    def check_others(self):
        basic_high_super = [False, False, False]
        for i in (0, 1, 2):
            if self._urls[i]:
                basic_high_super[i] = True
        _check_others(basic_high_super, self.variety)


def print_result(tasks_info, filename, filenames, total_time):
    _total_time = 0
    download_bytes = 0
    length = 0
    try:
        for f in filenames:
            task_info = tasks_info[f]
            if task_info[0]:
                _total_time += task_info[2]
                download_bytes += sum(map(lambda t: t[4], task_info[4].values()))
                length += task_info[3]
            else:
                _total_time = task_info[2]
                download_bytes = task_info[3]
    except KeyError:
        print("Analysing the information of the downloaded file failed, because download has error.\n")
    else:
        if not _total_time:
            _total_time = total_time
        print(download.result(filename, _total_time, download_bytes, length), end='\n\n')
        
def usage(program_name):
    """
    Print the usage of the program.
    @program_name:  the name of this program
    """
    print("")
    print("Usage:")
    print("      {} [-b] [-h] [-H] [-s] [URL] [filename]\n".format(program_name))
    print("-h")
    print("    Print the help information.\n")
    print("-b")
    print("    Download the basic vedio.\n")
    print("-H")
    print("    Download the high vedio.\n")
    print("-s")
    print("    Download the super vedio.\n")
    print("URL")
    print("    the address where you will download what you want.\n")
    print("filename")
    print("    the name of the file used to save what you will download.\n")
    sys.exit(os.EX_OK)

if __name__ == "__main__":
    url = ''
    filename = ''
    
    # Handle the argument from the command line.
    try:
        options, args = getopt.getopt(sys.argv[1:], "bhHs")
    except getopt.GetoptError:
        usage(os.path.split(sys.argv[0])[1])
    opt_url = 0
    for opt, val in options:
        if opt == '-b':
            opt_url = 0
        elif opt == '-H':
            opt_url = 1
        elif opt == '-s':
            opt_url = 2
        else:
            usage(os.path.split(sys.argv[0])[1])
    arg_len = len(args)
    if arg_len > 0:
        url = args[0]
    if arg_len > 1:
        filename = args[1]
    if not url:
        print("Please give the URL.")
        sys.exit(os.EX_OK)

    # Get the real URL of the file which you want to download.
    parser = FLVCD(url, opt_url)
    #parser = FLVXZ(url, opt_url)
    print("Parse the URL ...") 
    urls = parser.parse_url()
    if urls is None:
        print("Can't parse the URL: {}".format(url))
        sys.exit(os.EX_OK)
    
    # Check whether there are other kind of videos.
    if not urls:
        parser.check_others(opt_url)
        sys.exit(os.EX_OK)

    # Get the total size of which you want to download.
    total_size = 0
    _urls = []
    for u in urls:
        try:
            con = urlopen(u)
        except error.URLError:
            continue
        _urls.append(u)
        total_size += int(con.headers.get("Content-Length", 0))
        con.close()
    urls = _urls
    if total_size == 0:
        print("This file can't be downloaded.")
        sys.exit(os.EX_OK)
        
    # Each real URL corresponds with a filename.
    if not filename:
        url_split = urlparse(url)
        name = os.path.split(url_split.path)[1]
        filename = name if name else url_split.netloc
    if not os.path.split(filename)[0]:
        filename = os.path.join(directory_to_save_file, filename)
    filename = os.path.abspath(os.path.expanduser(filename))
    dir_  = os.path.dirname(filename)
    file_ = os.path.basename(filename)
    loc = file_.rfind('.')
    if loc == -1:
        mk_dir = filename
    else:
        mk_dir = os.sep.join((dir_, file_[:loc]))
    try:
        os.makedirs(mk_dir)
    except OSError:
        pass
    filename = os.sep.join((mk_dir, file_))
    if os.path.lexists(filename):
        y_or_n = input("{} has existed. Do you download it again? (y or n) ".format(filename))
        while y_or_n not in ('y', 'Y', 'N', 'n'):
            y_or_n = input("Please input (y or n): ")
        if y_or_n in ('n', 'N'):
            print("Exit ...\n")
            sys.exit(os.EX_OK)
    
    if len(urls) < 2:
        filenames = [filename]
    else:
        if loc == -1:
            filenames = ['{}_{:02d}'.format(filename, i) for i in range(1, len(urls)+1)]
        else:
            dot_loc = filename.rfind('.')
            filenames = ['{}_{:02d}{}'.format(filename[:dot_loc], i, filename[dot_loc:]) for i in range(1, len(urls)+1)]
        print("This file is divided into {:d} parts".format(len(filenames)))

    print("Start to download ...")
    try:
        task = Thread(target=download.download, args=(urls, filenames, temp_download_directory, 10, True, False))
    except (SystemExit, KeyboardInterrupt):
        print("Exit ...")
        sys.exit(os.EX_OK)
    except Exception:
        print("Sorry! The program has a exception, and the author will modify it.")
    else:
        task.start()
        start_time = time.time()
        download.watch_files(filename, filenames, task, total_size)
        # Analyse the result.
        total_time = int(time.time() - start_time)
        print_result(download.get_tasks_info(), filename, filenames, total_time)

