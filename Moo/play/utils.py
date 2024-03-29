'''
Moo Utilities
~~~~~~~~~~~~~
'''

import os
import math
import time


def file_age(filepath):
    '''
    returns seconds since filepath modified (mtime)
    '''
    if os.path.exists(filepath):
        return int(time.time() - os.path.getmtime(filepath))
    else:
        return None


def hours_minutes(seconds, colons=False):
    '''returns h(ours) m(inutes) from seconds'''
    out = list()
    minute = 60
    hour = 60 * minute

    if seconds >= hour:
        hours = math.floor(seconds / hour)
        seconds = seconds % hour
        if colons:
            out.append(str(hours).zfill(2))
        else:
            out.append('{}h'.format(hours))

    if seconds >= minute:
        minutes = math.ceil(seconds / minute)
        if colons:
            out.append(str(minutes).zfill(2))
        else:
            out.append('{}m'.format(minutes))
        seconds = seconds % minute
    else:
        if colons:
            out.append('00')

    # if seconds:
    #     if colons:
    #         out.append(str(seconds).zfill(2))
    #     else:
    #         out.append('{}s'.format(seconds))
    # else:
    #     if colons:
    #         out.append('00')

    if colons:
        return ":".join(out)

    return "".join(out)
