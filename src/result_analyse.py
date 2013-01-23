# Copyright (C) xgfone 2012 - 2013
# -*- coding: utf-8 -*-

__all__ = ["analyse_result", "result", "format_bytes", "format_time"]

_KB = 1024
_MB = _KB * _KB
_GB = _MB * _KB
_TB = _GB * _KB
_MINUTE   = 60
_HOUR  = _MINUTE * 60
_DAY = _HOUR * 24

def format_bytes(byte_number:int):
    rtn = [0, 0, 0, 0]  # [TB, GB, MB, KB]
    if byte_number > _TB:    
        rtn[0] = byte_number / _TB
    elif byte_number > _GB:
        rtn[1] = byte_number / _GB
    elif byte_number > _MB:
        rtn[2] = byte_number / _MB
    elif byte_number > _KB:
        rtn[3] = byte_number / _KB
    return rtn

def format_time(sec_number:int):
    rtn = [0, 0, 0, 0]  # [day, hour, minute, second]
    rtn[0] = sec_number // _DAY
    hour   = sec_number % _DAY
    rtn[1] = hour // _HOUR
    minute = hour % _HOUR
    rtn[2] = minute // _MINUTE
    rtn[3] = minute % _MINUTE
    return rtn

def result(filename, total_time, download_bytes, length=None):
    """
    Print the formated statistics.
    """
    rtn = '\n'
    if not download_bytes or not length:
        rtn = ''.join((rtn, "{} completed. ".format(filename)))
    else:
        if length == download_bytes:
            rtn = ''.join((rtn, "{} complete normally. ".format(filename)))
        else:
            rtn = ''.join((rtn, "{} complete unnormally, and miss {:d} bytes. ".format(filename, length - download_bytes)))

    size = format_bytes(download_bytes)
    if size[0]:
        rtn = ''.join((rtn, "Download {:.2f}TB, ".format(size[0])))
    elif size[1]:
        rtn = ''.join((rtn, "Download {:.2f}GB, ".format(size[1])))
    elif size[2]:
        rtn = ''.join((rtn, "Download {:.2f}MB, ".format(size[2])))
    elif size[3]:
        rtn = ''.join((rtn, "Download {:.2f}KB, ".format(size[3])))
    else:
        rtn = ''.join((rtn, "Download {:d}B, ".format(download_bytes)))

    if total_time == 0:
        rtn = ''.join((rtn, "Cost 0s\n"))
        return rtn

    times = format_time(total_time)
    if times[0]:
        rtn = ''.join((rtn, "Cost {0:d}d {1:d}h {2:d}m {3:d}s, ".format(times[0], times[1], times[2], times[3])))
    elif times[1]:
        rtn = ''.join((rtn, "Cost {0:d}h {1:d}m {2:d}s, ".format(times[1], times[2], times[3])))
    elif times[2]:
        rtn = ''.join((rtn, "Cost {0:d}m {1:d}s, ".format(times[2], times[3])))
    else:
        rtn = ''.join((rtn, "Cost {0:d}s, ".format(times[3])))

    speed_byte = download_bytes / total_time
    speed = format_bytes(speed_byte)
    if speed[0]:
        rtn = ''.join((rtn, "{:.2f} TB/S".format(speed[0])))
    elif speed[1]:
        rtn = ''.join((rtn, "{:.2f} GB/S".format(speed[1])))
    elif speed[2]:
        rtn = ''.join((rtn, "{:.2f} MB/S".format(speed[2])))
    elif speed[3]:
        rtn = ''.join((rtn, "{:.2f} KB/S".format(speed[3])))
    else:
        rtn = ''.join((rtn, "{:.2f} B/S".format(speed_byte)))
    return rtn

def analyse_result(tasks_info, filename):
    if tasks_info[filename][0]:
        #sorted(tasks_info[filename][4].items(), key=lambda i: i[0])
        download_bytes = sum(map(lambda t: t[4], tasks_info[filename][4].values()))
        return result(filename, tasks_info[filename][2], download_bytes, tasks_info[filename][3])
    else:
        return result(filename, tasks_info[filename][2], tasks_info[filename][3])


