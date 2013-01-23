Download
========

A downloader to download what you want to, and a video downloader front end.


Introduction
    
    You only care and use the "download.py" and "flv_download.py" modules.

    download.py -- a multiprocessing or multithreading downloader used to download what you want. You consider it as
    Xunlei, FlashGet, or other downloader.
    flv_download.py -- a downloader used to download the flv video from other website with the download.py downloader
    above.

    flv_download.py support www.youku.com, www.ku6.com, www.tudou.com, v.qq.com, www.56.com, v.163.com, www.letv.com, 
    www.cctv.com, v.ifeng.com, www.m1905.com, video.sina.com.cn, www.kugou.com, kankan.xunlei.com(partial), and so on.

    Only if the website(www.flvcd.com) can parse it, this program can download the file. Thank for www.flvcd.com.
    
    More introduction, please see "doc/*".

Requirement

    Before use, please install the python programming language(>=3) and the BeautifulSoup package(>=4).

Use

    download [-dhnv][-D dir][-N number][-b breakpoint] [URL] [filename]
    flv_download [-b] [-h] [-H] [-s] [URL] [filename]
 
Example

    (1) Download the python-3.3.0:
    download.py http://211.136.8.17/files/922200000009098C/www.python.org/ftp/python/3.3.0/python-3.3.0.msi python.msi
    or
    download.py http://211.136.8.17/files/922200000009098C/www.python.org/ftp/python/3.3.0/python-3.3.0.msi


    (2) Download the a flv video from www.youku.com:
    flv_download.py http://v.youku.com/v_show/id_XNDk3MzUwMzYw.html 大师.flv

    Download the high version:
    flv_download.py -H http://v.youku.com/v_show/id_XNDk3MzUwMzYw.html 大师.flv

    Download the super version:
    flv_download.py -s http://v.youku.com/v_show/id_XNDk3MzUwMzYw.html 大师.flv

    NOTICE:
    If you don't want to give the URL and filename, you can find "filename" and "url" which are below 
    "if __name__ == '__main__':", and assign them with URL and filename.

 
