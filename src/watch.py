# Copyright (C) xgfone 2012-2013
# -*- coding: utf-8 -*-
from __future__ import division, print_function

import time
import result_analyse
import downloader_handle

__all__ = ["watch", "watch_files"]

def _print_watch_result(filename, downloaded_number, number, interval_time, used_time, total_size, finish=False):
    rtn = '\r'
    if finish:
        rtn += _('{0} has download, integrating the file ...').format(filename)
        return rtn

    if total_size == 0:
        rtn_byte = result_analyse.format_bytes(downloaded_number)
        if rtn_byte[0]:
            rtn = ''.join((rtn, _("{0} downloaded {1:.2f} TB, ").format(filename, rtn_byte[0])))
        elif rtn_byte[1]:
            rtn = ''.join((rtn, _("{0} downloaded {1:.2f} GB, ").format(filename, rtn_byte[1])))
        elif rtn_byte[2]:
            rtn = ''.join((rtn, _("{0} downloaded {1:.2f} MB, ").format(filename, rtn_byte[2])))
        elif rtn_byte[3]:
            rtn = ''.join((rtn, _("{0} downloaded {1:.2f} KB, ").format(filename, rtn_byte[3])))
        else:
            rtn = ''.join((rtn, _("{0} downloaded {1:d}B, ").format(filename, downloaded_number)))
    else:
        rtn = ''.join((rtn, (_("{0} completes({1:05.2f}%), ")).format(filename, downloaded_number*100/total_size)))

    speed_byte = int(number / interval_time)
    speed = result_analyse.format_bytes(speed_byte)
    rtn_time = result_analyse.format_time(used_time)
    
    if rtn_time[0]:
        rtn = ''.join((rtn, _("Cost {0:d}d {1:d}h {2:d}m {3:d}s, ").format(rtn_time[0], rtn_time[1], rtn_time[2], rtn_time[3])))
    elif rtn_time[1]:
        rtn = ''.join((rtn, _("Cost {0:d}h {1:d}m {2:d}s, ").format(rtn_time[1], rtn_time[2], rtn_time[3])))
    elif rtn_time[2]:
        rtn = ''.join((rtn, _("Cost {0:d}m {1:d}s, ").format(rtn_time[2], rtn_time[3])))
    else:
        rtn = ''.join((rtn, _("Cost {0:d}s, ").format( rtn_time[3])))
        
    if total_size != 0:
        if speed_byte == 0:
            rtn = ''.join((rtn, _("Unknown remained time,")))
        else:
            remain_bytes = total_size - downloaded_number
            remain_time  = result_analyse.format_time(int(remain_bytes / speed_byte))
            if remain_time[0]:
                rtn = ''.join((rtn, _("Remain {0:d}d {1:d}h {2:d}m {3:d}s, ").format(remain_time[0], remain_time[1], remain_time[2], remain_time[3])))
            elif remain_time[1]:
                rtn = ''.join((rtn, _("Remain {0:d}h {1:d}m {2:d}s, ").format(remain_time[1], remain_time[2], remain_time[3])))
            elif remain_time[2]:
                rtn = ''.join((rtn, _("Remain {0:d}m {1:d}s, ").format(remain_time[2], remain_time[3])))
            else:
                rtn = ''.join((rtn, _("Remain {0:d}s, ").format(remain_time[3])))
        
    if speed[0]:
        rtn = ''.join((rtn, _("{0:.2f} TB/S").format(speed[0])))
    elif speed[1]:
        rtn = ''.join((rtn, _("{0:.2f} GB/S").format(speed[1])))
    elif speed[2]:
        rtn = ''.join((rtn, _("{0:.2f} MB/S").format(speed[2])))
    elif speed[3]:
        rtn = ''.join((rtn, _("{0:.2f} KB/S").format(speed[3])))
    else:
        rtn = ''.join((rtn, _("{0:.2f} B/S").format(speed_byte)))
    
    return rtn


def watch(filename, download_thread):
    sleep_time = 2
    real_sleep_time = sleep_time - 0.1
    start_time = time.time()
    last_downloaded_number = 0
    last_output_len = 0

    # Ensure that the tasks information is not empty.
    tasks_info = downloader_handle.get_tasks_info(filename)
    while download_thread.is_alive() and not tasks_info:
        tasks_info = downloader_handle.get_tasks_info(filename)
    # Extract the total size of the file
    total_size = 0
    while download_thread.is_alive():
        tasks_info = downloader_handle.get_tasks_info(filename)
        # If doesn't determine the download manner, continue.
        if tasks_info[filename][0] is None:
            continue
        if tasks_info[filename][0]:
            # Ensure no KeyError
            while True:
                try:
                    total_size = tasks_info[filename][3]
                except KeyError:
                    pass
                else:
                    if total_size:
                        break
                    tasks_info = downloader_handle.get_tasks_info(filename)
        break

    while download_thread.is_alive(): 
        end_time = time.time()
        total_time = int(end_time - start_time)
        if not total_time:
            continue
        tasks_info = downloader_handle.get_tasks_info(filename)
        
        if total_size:
            downloaded_number = sum(map(lambda v: v[4], tasks_info[filename][4].values()))
            is_finish = False
            for v in tasks_info[filename][4].values():
                if v[3] == v[4]:
                    is_finish = True
                    break
        else:
            downloaded_number = tasks_info[filename][3]
            is_finish = False
            
        number = downloaded_number - last_downloaded_number
        last_downloaded_number = downloaded_number

        print('\r', ' ' * last_output_len, end='')
        rtn = _print_watch_result(filename, downloaded_number, number, sleep_time, total_time, total_size, is_finish)
        last_output_len = len(rtn) + 25
        print(rtn, end='')
        time.sleep(real_sleep_time)


def watch_files(filename, filenames, download_thread, total_size):
    sleep_time = 2
    real_sleep_time = sleep_time - 0.1
    start_time = time.time()
    last_downloaded_number = 0
    last_output_len = 0

    # Ensure that the tasks information is not empty.
    tasks_info = downloader_handle.get_tasks_info(filenames)
    while download_thread.is_alive() and not tasks_info:
        tasks_info = downloader_handle.get_tasks_info(filenames)
    
    while download_thread.is_alive():
        total_time = int(time.time() - start_time)
        if not total_time:
            continue
        tasks_info = downloader_handle.get_tasks_info(filenames)

        downloaded_number = 0
        for f in filenames:
            if tasks_info[f][0]:
                downloaded_number += sum(map(lambda v: v[4], tasks_info[f][4].values()))
                is_finish = False
                for v in tasks_info[filename][4].values():
                    if v[3] == v[4]:
                        is_finish = True
                        break
            else:
                downloaded_number += tasks_info[f][3]
                is_finish = False

        number = downloaded_number - last_downloaded_number
        last_downloaded_number = downloaded_number

        print('\r', ' ' * last_output_len, end='')
        rtn = _print_watch_result(filename, downloaded_number, number, sleep_time, total_time, total_size, is_finish)
        last_output_len = len(rtn) + 25
        print(rtn, end='')
        time.sleep(real_sleep_time)


