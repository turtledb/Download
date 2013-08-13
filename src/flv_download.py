#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# REQUIREMENT:
#           (1)Python3 --- an interpreter programming language, >= 3.
#           (2)BeautifulSoup4 --- a python package, >= 4.
#           (3)download ---- a module, which downloads a file through the multiprocessing
#              or the multithreading.
#
# FUNCTION: Download the flv video coming from www.youku.com.
#
# PROBLEM:
#           (1) If it can't download what you want, please first check whether the URL
#               which you gave is probably parsed by www.flvcd.com. If parsed, please
#               contact me; if not, it indicates that what you want can't be downloaded.
#           (2) The class "FLVXZ" can't work successfully. urllib.request.urlopen can't
#               acquire the whole result website. So it must use a especial way. I hope
#               someone to solve it. I will give the interface later.
#
from __future__ import print_function

import re
import os
import sys
import bs4
import time
import getopt

import py3or2
import download
if py3or2.PY3:
    from urllib.error import URLError
    from urllib.request import urlopen
    from urllib.parse import urlparse
else:
    from urllib2 import URLError, urlopen
    from urlparse import urlparse

try:
    from threading import Thread
except ImportError:
    from dummy_threading import Thread


__version__ = "0.2.2"
__author__  = "xgfone <xgfone@126.com>"
__copyright__ = "Copyright (C) 2012 - 2013, xgfone"
__contributors__ = []
__license__ = "MIT"

directory_to_save_file = download.directory_to_save_file
temp_download_directory = download.temp_directory_to_save_file


def _check_others(basic_high_super, variety):
    index_ = (0, 1, 2)
    opt = ('b', 'H', 's')
    content = (_("basic"), _("high"), _("super"))
    print(_("There is not the {0} video.").format(content[variety]))

    tmp_ = 0
    for i in index_:
        if basic_high_super[i]:
            tmp_ += 1

    if tmp_ == 0:
        if variety == 0:
            print(_("There are also not the high video and the super."))
        elif variety == 1:
            print(_("There are also not the basic video and the super."))
        else:
            print(_("There are also not the basic video and the high."))
    elif tmp_ == 1:
        for i in index_:
            if basic_high_super[i]:
                print(_("There is the {0} video, and you can use the -{1} option.").format(content[i], opt[i]))
                break
    elif tmp_ == 2:
        for i in index_:
            if basic_high_super[i]:
                print(_("There is the {0} video(the option: -{1}), and ").format(content[i], opt[i]), end='')
                break
        for j in index_:
            if j != i and basic_high_super[j]:
                print(_("the {0} video(the option: -{1}).").format(content[i], opt[i]))
                break
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
        except (URLError, IndexError):
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
        except (URLError, IndexError):
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
        print(_("Analysing the information of the downloaded file failed, because download has error."), end='\n\n')
    else:
        if not _total_time:
            _total_time = total_time
        print(download.result(filename, _total_time, download_bytes, length), end='\n\n')


def usage(program_name):
    """
    Print the usage of the program.
    @program_name:  the name of this program
    """
    print(__copyright__)
    print(_("Usage:"))
    print("      {0} [-bhsH] [-n NUM] [-N NUM] [URL] [filename]".format(program_name))
    print(_("      Download FLV video from other video websites."), end='\n\n')
    print("-h")
    print(_("    Print the help information."), end='\n\n')
    print("-b")
    print(_("    Download the basic vedio."), end='\n\n')
    print("-H")
    print(_("    Download the high vedio."), end='\n\n')
    print("-s")
    print(_("    Download the super vedio."), end='\n\n')
    print("-n NUM")
    print(_("    Download from NUMth part to the end."), end='\n\n')
    print("-N NUM")
    print(_("    Only download NUMth part."), end='\n\n')
    print("URL")
    print(_("    the address where you will download what you want."), end='\n\n')
    print("filename")
    print(_("    the name of the file used to save what you will download."), end='\n\n')
    sys.exit(os.EX_OK)


if __name__ == "__main__":
    import local
    import locale
    locale.setlocale(locale.LC_ALL, '')
    local.install_gettext("messages")

    url = ''
    filename = ''

    # Handle the argument from the command line.
    try:
        options, args = getopt.getopt(sys.argv[1:], "bhHsn:N:")
    except getopt.GetoptError:
        usage(os.path.split(sys.argv[0])[1])
    opt_url = 0
    nth_part = 1
    Nth_part = 1
    n_or_N = 'n'
    for opt, val in options:
        if opt == '-b':
            opt_url = 0
        elif opt == '-H':
            opt_url = 1
        elif opt == '-s':
            opt_url = 2
        elif opt == '-n':
            val = int(val)
            if val > 1:
                nth_part = val
                n_or_N = 'n'
        elif opt == '-N':
            val = int(val)
            if val > 1:
                Nth_part = val
                n_or_N = 'N'
        else:
            usage(os.path.split(sys.argv[0])[1])
    arg_len = len(args)
    if arg_len > 0:
        url = args[0]
    if arg_len > 1:
        filename = args[1]
    if not url:
        print(_("Please give the URL."))
        sys.exit(os.EX_OK)

    # Get the real URL of the file which you want to download.
    parser = FLVCD(url, opt_url)
    #parser = FLVXZ(url, opt_url)
    print(_("Parse the URL ..."))
    urls = parser.parse_url()
    if urls is None:
        print(_("Can't parse the URL: {0}").format(url))
        sys.exit(os.EX_OK)

    # Check whether there are other kind of videos.
    if not urls:
        parser.check_others()
        sys.exit(os.EX_OK)

    # Correct the filename.
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

    # Judge whether the file exists.
    if os.path.lexists(filename):
        y_or_n = input(_("{0} has existed. Do you download it again? (y or n) ").format(filename))
        while y_or_n not in ('y', 'Y', 'N', 'n'):
            y_or_n = input(_("Please input (y or n): "))
        if y_or_n in ('n', 'N'):
            print(_("Exit ..."))
            sys.exit(os.EX_OK)

    # Ensure each filename correspond to each url.
    url_len = len(urls)
    if url_len < 2:
        filenames = [filename]
        print(_("This file has totally one part."))
    else:
        if loc == -1:
            filenames = ['{0}_{1:d}_{2:02d}'.format(filename, url_len, i) for i in range(1, len(urls)+1)]
        else:
            dot_loc = filename.rfind('.')
            filenames = ['{0}_{1:d}_{2:02d}{3}'.format(filename[:dot_loc], url_len, i, filename[dot_loc:]) for i in range(1, len(urls)+1)]
        print(_("This file is divided into {0:d} parts.").format(len(filenames)))

    if n_or_N == 'n':
        if url_len > nth_part:
            _nth_part = nth_part - 1
            urls = urls[_nth_part:]
            filenames = filenames[_nth_part:]
    else:
        if url_len > Nth_part:
            _Nth_part = Nth_part - 1
            urls = urls[_Nth_part:Nth_part]
            filenames = filenames[_Nth_part:Nth_part]
            nth_part = Nth_part

    print(_("Start to download ..."))
    start_time = time.time()
    try:
        for i, u_f in enumerate(zip(urls, filenames), nth_part):
            if url_len > 1:
                print(_("Downloading the {0:d}th part ...").format(i))
            task = Thread(target=download.download, args=(u_f[0], u_f[1]))
            task.start()
            download.watch(u_f[1], task)
            task.join()
    except (KeyboardInterrupt, SystemExit):
        print()
        print(_("Exit ..."))
    except Exception:
        print()
        print(_("Sorry! The program has a exception, and the author will modify it."))
    else:
        if url_len == len(urls):
            total_time = int(time.time() - start_time)
            print()
            print_result(download.get_tasks_info(), filename, filenames, total_time)
