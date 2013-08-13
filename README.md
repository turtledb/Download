Download
========

A downloader to download what you want to, and a video downloader front end.


Introduction
    
    You only care and use the "download.py" and "flv_download.py" modules.

    download.py -- a multiprocessing or multithreading downloader used to download what you want. You consider it as
    Xunlei, FlashGet, or other downloader.
    flv_download.py -- a downloader used to download the flv video from other website with the download.py downloader
    above.

    flv_download.py support www.youku.com, and doesn't support www.tudou.com and www.iqiyi.com. The three websites is
    tested, but others websites is not tested.

    More introduction, please see "doc/*".

Requirement

    Before use, please install the python programming language(>=2.6) and the BeautifulSoup package(>=4). But if
    only using download.py, not need BeautifullSoup4, and only flv_download.py needs it. Now, these support 
    python 2.6, 2.7, and 3.X. Below 2.6, such as 2.5, I don't test; because these versions are too old, and I
    don't want to support them.

Use

    download [-dhn][-D dir][-N number][-b breakpoint] [URL] [filename]
    flv_download [-bhsH] [-n NUM] [-N NUM] [URL] [filename]
 
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

 
