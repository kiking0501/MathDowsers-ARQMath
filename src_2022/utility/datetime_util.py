# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse as _dateparse
import re


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


def dt_midnight(ts):
    return str2dt(ts).replace(hour=0, minute=0, second=0, microsecond=0)


def dt_roundup_midnight(ts):
    result = str2dt(ts).replace(hour=0, minute=0, second=0, microsecond=0)
    if result < str2dt(ts):
        result += timedelta(days=1)
    return result


def dt_rounddown(ts, minutes):
    ''' round down to the lastest datetime from ts
        that has a multiple of the input minutes since midnight '''
    ts = str2dt(ts)
    before = ts.hour * 60 + ts.minute
    after = before - before % minutes
    return ts.replace(hour=after / 60, minute=after % 60, second=0, microsecond=0)


def dt_roundup(ts, minutes):
    ''' round up to the lastest datetime from ts
        that has a multiple of the input minutes since midnight '''

    new_ts = dt_rounddown(ts, minutes)
    if new_ts < str2dt(ts):
        new_ts += timedelta(minutes=minutes)
    return new_ts


def dt_forward(ts, **delta):
    ''' increase datetime by delta '''
    return str2dt(ts) + timedelta(**delta)


def dt_backward(ts, **delta):
    ''' decrease datetime by delta '''
    return str2dt(ts) - timedelta(**delta)


def dt_slice(start, end, MAX=100000000, **delta):
    ''' get a list of datetime-obj from start to end, differ by delta

        use MAX to control max number of datetime-obj returned '''
    start, end, delta = str2dt(start), str2dt(end), timedelta(**delta)
    if start == end:
        return [start]

    curr, res = start, []

    for _ in range(MAX):

        if curr > end:
            break

        res.append(curr)
        curr += delta

    else:
        raise RuntimeError("Loop number exceeds %d; Please change the MAX limit! " % MAX)

    return res


def dt2str(ts, format_='%Y-%m-%d %H:%M:%S', empty=''):
    if isinstance(ts, datetime):
        return ts.strftime(format_)
    if ts is None:
        return empty
    return ts  # assume str


class DateBinning(object):
    ''' Group a date range in to bins '''

    def __init__(self, dates, num_dates=7, bin_from='end'):
        ''' @param datas: list of dates, only min / max in list are used
            @param num_dates: group how many dates into a bin
            @param whether the first bin is grouped from start or end
        '''
        self.min_date = self.trunc_date(min(dates))
        self.max_date = self.trunc_date(max(dates))
        self.num_dates = num_dates
        if bin_from != 'end':
            raise NotImplementedError()
        self.bin_from = bin_from

    def index(self):
        ''' return all the bin index '''
        curr = self.max_date - timedelta(days=self.num_dates - 1)
        results = []
        while curr + timedelta(days=self.num_dates - 1) >= self.min_date:
            results.append(curr)
            curr -= timedelta(days=self.num_dates)
        return sorted(results)

    def find_bin(self, date):
        ''' find bin index of a specific date '''
        date = self.trunc_date(date)
        last_start = self.max_date - timedelta(days=self.num_dates - 1)
        adjust_days = (date - last_start).days % self.num_dates
        return date - timedelta(days=adjust_days)

    def trunc_date(self, d):
        ''' remove hour minutes '''
        if isinstance(d, datetime):
            d = d.date()
            return datetime(d.year, d.month, d.day)
        return d


class DateGrouping(DateBinning):
    ''' TODO: implement test, integrate with DateBinning '''

    def __init__(self, dates, group_by='month'):
        ''' group_by = day, week, month '''
        self.min_date = self.trunc_date(min(dates))
        self.max_date = self.trunc_date(max(dates))
        self.group_by = group_by

    def index(self):
        results = []
        if self.group_by == 'day':
            curr = self.min_date
            while curr <= self.max_date:
                results.append(curr)
                curr += timedelta(days=1)
        elif self.group_by == 'week':
            curr = self.min_date
            curr = curr - timedelta(days=curr.weekday())  # to monday
            while curr <= self.max_date:
                results.append(curr)
                curr += timedelta(days=7)
        elif self.group_by == 'month':
            curr = self.min_date
            curr = datetime(curr.year, curr.month, 1)
            while curr <= self.max_date:
                results.append(curr)
                curr += relativedelta(months=1)
        else:
            raise ValueError()
        return results

    def find_bin(self, date):
        date = self.trunc_date(date)
        if self.group_by == 'day':
            return date
        elif self.group_by == 'week':
            return date - timedelta(days=date.weekday())
        elif self.group_by == 'month':
            return datetime(date.year, date.month, 1)


def datetime_unaware(d):
    ''' remove microsecond of datetime object (without timezone) '''
    return datetime(*d.timetuple()[:6])


def db_to_datetime(d):
    ''' change db datetime to local unaware datetime '''
    from django.utils.timezone import localtime
    return datetime_unaware(localtime(d))


def datetime_local(*args, **kwargs):
    ''' change a datetime to datetime with localtime zone set
        can either pass a datetime / construct like datetime '''
    from django.utils.timezone import get_current_timezone
    if args and isinstance(args[0], (date, datetime)):
        return get_current_timezone().localize(args[0])
    else:
        return get_current_timezone().localize(datetime(*args))

# def datetime_local(*args, **kwargs):
#     ''' change a datetime to datetime with localtime zone set
#         can either pass a datetime / construct like datetime '''
#     from django.utils.timezone import get_current_timezone
#     if args and isinstance(args[0], (date, datetime)):
#         return datetime(*args[0].timetuple()[:6], tzinfo=get_current_timezone())
#     else:
#         return datetime(*args, tzinfo=get_current_timezone(), **kwargs)


_re_dayfirst = re.compile('\d{1,2}[/.]\d{1,2}[/.]\d{2,4}|\d{1,2}-\d{1,2}-\d{4}')


def dateparse(timestr, parserinfo=None, **kwargs):
    ''' dateparse for normal usage since python dateparse will parse:
            03/05/2016 -> 05 March 2016
            03.05.2016 -> 05 March 2016
        which are uncommon in Hong Kong

        This function auto add dayfirst=True if it match these format
    '''
    if _re_dayfirst.match(timestr) and 'dayfirst' not in kwargs:
        kwargs['dayfirst'] = True
    return _dateparse(timestr, parserinfo=None, **kwargs)


def convert_to_dateRange(start_date, end_date, date_type, date_val):
    ''' monitor: a time cutoff to return two date range with date_val in middle
        ... : TODO: finish it

        month: YYYY-MM

        return 4-tuple:
            range_A_start, range_A_end, range_B_start, range_B_end
        * end date is one off the end
    '''

    startDateStart = None
    startDateEnd = None
    endDateStart = None
    endDateEnd = None

    if date_type == "day":
        startDateStart = start_date
        endDateEnd = end_date
        startDateEnd = datetime.strptime(date_val, '%Y-%m-%d')
        endDateStart = startDateEnd
    elif date_type == "wow":
        date = datetime.strptime(date_val, '%Y-%m-%d')
        startDateStart = date - timedelta(days=7)
        startDateEnd = date
        endDateStart = startDateEnd
        endDateEnd = endDateStart + timedelta(days=7)
    elif date_type == "mom":
        if date_val == 'latest':
            date = [end_date.year, end_date.month]
        else:
            date = date_val.split("-")
        endDateStart = datetime(int(date[0]), int(date[1]), 1)
        endDateEnd = endDateStart + relativedelta(months=1)
        startDateEnd = endDateStart
        startDateStart = startDateEnd - relativedelta(months=1)
    elif date_type == "qoq":
        date = date_val.split("Q")
        endDateStart = datetime(int(date[0]), 3 * int(date[1]) - 2, 1)
        endDateEnd = endDateStart + relativedelta(months=3)
        startDateEnd = endDateStart
        startDateStart = startDateEnd - relativedelta(months=3)
    elif date_type == "yoy":
        if date_val == 'latest':
            date = [end_date.strftime('%Y-%m-01'), end_date.strtime('%Y-%m-%d')]
        else:
            date = date_val.split(",")
        endDateStart = datetime.strptime(date[0], '%Y-%m-%d')
        endDateEnd = datetime.strptime(date[1], '%Y-%m-%d') + relativedelta(days=1)
        startDateStart = endDateStart - relativedelta(years=1)
        startDateEnd = endDateEnd - relativedelta(years=1)
    else:
        raise NotImplementedError("TODO")

    if start_date is not None:
        startDateStart = max(start_date, startDateStart)
        endDateStart = max(start_date, endDateStart)
    if end_date is not None:
        startDateEnd = min(end_date, startDateEnd)
        endDateEnd = min(end_date, endDateEnd)

    return startDateStart, startDateEnd, endDateStart, endDateEnd


def cal_last_date(datetime_obj, date_type='month'):
    if date_type == 'month':
        adjust_dt = datetime_obj - relativedelta(months=1)
        return datetime(adjust_dt.year, adjust_dt.month, 1)
    elif date_type == 'quarter':
        adjust_dt = datetime_obj - relativedelta(months=3)
        month = adjust_dt.month - (adjust_dt.month - 1) % 3
        return datetime(adjust_dt.year, month, 1)
    elif date_type == 'year':
        adjust_dt = datetime_obj - relativedelta(years=1)
        return datetime(adjust_dt.year, 1, 1)
    else:
        raise ValueError("Unknown date_type: %s" % date_type)
