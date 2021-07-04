# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from datetime import datetime


TIME_FORMATS = [
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%dT%H:%M:%S.%fZ',
    '%Y-%m-%dT%H:%M:%S.%f',
    '%Y-%m-%dT%H:%M:%SZ',
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%d %H:%M',
    '%Y-%m-%d-%H:%M',
    '%Y%m%d',
    '%Y%m%d%H',  # if check earlier than '%Y%m%d', '20180811' would be recognize as 2018-08-01 0100
    '%Y%m%d%H%M',
    '%Y-%m-%d-%H',
    '%Y/%m/%d-%H:%M',
    '%Y/%m/%d-%H',
    '%Y-%m-%d',
    '%Y/%m/%d',
    '%Y-%m',
    '%Y/%m',
    '%y-%m-%d %H:%M',
]


def str2dt(time_obj, suppress_error=False):
    ''' convert time-string to datetime obj '''

    if not isinstance(time_obj, datetime):
        for t in TIME_FORMATS:
            try:
                time_obj = datetime.strptime(time_obj, t)
                break
            except Exception:
                continue

    if not isinstance(time_obj, datetime):
        if not suppress_error:
            raise ValueError('Invalid object: "%s". Please input time_obj in '
                             'datetime.datetime obj, or in str-obj %s!' % (time_obj, TIME_FORMATS))
        else:
            return  # return None
    return time_obj


def dt2str(ts, format_='%Y-%m-%d %H:%M:%S', empty=''):
    if isinstance(ts, datetime):
        return ts.strftime(format_)
    if ts is None:
        return empty
    return ts  # assume str
