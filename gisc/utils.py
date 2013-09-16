#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Generic use functions"""

import datetime
import os
import shutil
import time
import zipfile

from errors import (BadZIPError, DBPopulateError, InvalidArchFileError,
                    UnexpectedDateTimeStampError)

__author__ = "anshu.choubey@imaginea.com"

# Archives start date.
START_DATE = datetime.datetime(2011, 2, 12)


def parse_time(raw_time):
    """Parse date time string.

    :Parameters:
        - raw_time : str : String format date time stamp.
    :Raises:
        - UnexpectedDateTimeStampError if the input string is of any
        different format.
    :Returns:
        - datetime.datetime object : Parsed date time stamp.
    """
    try:
        return datetime.datetime.strptime(
            raw_time[:raw_time.rfind('-')], '%Y-%m-%dT%H:%M:%S')
    except Exception:
        return datetime.datetime.strptime(
            raw_time[:raw_time.rfind(' ')], '%Y/%m/%d %H:%M:%S')
    except Exception as e:
        raise UnexpectedDateTimeStampError('UNEXPECTED_DTSTAMP', raw_time, e)


def get_float_time(time_stamp):
    """Return float value of a date time stamp.

    :Parameters:
        - time_stamp : str or datetime.datetime object: Input date time
        stamp to be converted into float value.
    :Returns:
        - float : Float converted date time stamp value.
    """
    if isinstance(time_stamp, datetime.datetime):
        return time.mktime(time_stamp.timetuple())
    elif isinstance(time_stamp, basestring):
        return time.mktime(parse_time(time_stamp).timetuple())


def get_24_hrs_hence_datetime_str(time_stamp, sep=' '):
    """Return 24 hours hence date time stamp.

    :Parameters:
        - time_stamp : str or datetime.datetime object: Input date time
        stamp to be converted into float value.
        - sep : str : Separator between date and time. Defaults to ' '.
    :Returns:
        - str : 24 hours hence date time stamp.
    """
    if isinstance(time_stamp, datetime.datetime):
        time_limit = time_stamp + datetime.timedelta(days=1)
    elif isinstance(time_stamp, basestring):
        time_limit = parse_time(time_stamp) + datetime.timedelta(days=1)
    return unicode(time_limit.isoformat(sep))


def in_valid_date_range(date):
    """Check if a date is in the valid range.

    Github archives are available from 2012 Feb, 02. It checks if the
    date falls within the range from this date till today.
    :Parameters:
        - date : datetime.datetime object : Date time to validate.
    :Returns:
        - Boolean : True for in range, false otherwise.
    """
    return START_DATE < date < datetime.datetime.now()


def validate_date(arch_date):
    """Validate date as per the format yyyy-mm-dd-h[h].

    :Parameters:
        - arch_date : str : Date to be validated.

    @todo: Bad function and exception implementation.
    """
    # Check if every component of date is provided.
    try:
        y, m, d, h = arch_date.split('-')[:4]
    except ValueError:
        raise DBPopulateError('MISSING_VALUE', (arch_date,))
    # Create upper and lower bound dates.
    lower, upper = [], []
    for val in (y, m, d, h):
        val = val.strip('{}')
        delimiter = '..' in val and '..' or ',' in val and ',' or None
        left, right = delimiter and val.split(delimiter)[:2] or [val] * 2
        lower.append(left)
        upper.append(right)
    # Check if values are as per format.
    for k, v in zip(('lower', 'upper'), (lower, upper)):
        # Validate year.
        if len(v[0]) != 4:
            raise DBPopulateError('IMPROPER_VALUE', ('year', k, arch_date))
        for i, j in zip(('month', 'date'), v[1:3]):
#             @todo: Implement single digit month.
            if len(j) != 2:
                raise DBPopulateError('IMPROPER_VALUE', (i, k, arch_date))
    # Check if values entered are all integers.
    try:
        lower = map(int, lower)
        upper = map(int, upper)
    except ValueError, e:
        raise DBPopulateError('IMPROPER_TYPE', (arch_date,))
    # Check if date is valid.
    try:
        lower = datetime.datetime(*lower)
        upper = datetime.datetime(*upper)
    except ValueError, e:
        raise DBPopulateError(e)

    # Check if date corresponds to valid date bracket.
    if in_valid_date_range(lower) and in_valid_date_range(upper):
        return arch_date
    raise DBPopulateError('_OUT_BRACKET')


def download(url, path):
    """Download file from a URL and store at the designated path.

    :Parameters:
        - url : str : URL for the file to be downloaded.
        - path : str : Path where the file will be stored.
    """
    print url, path


def empty_directory(dir_path, create=True):
    """Delete and/or create a directory.

    :Parameters:
        - dir_path : str : Path of the directory to be emptied.
        - create : Boolean : If the directory should be created again.
        Defaults to True.
    """
    try:
        shutil.rmtree(dir_path)
    except OSError:
        pass
    if create:
        os.makedirs(dir_path)


def handle_valid_invalid_files(cmd_line_arg, dest):
    """Segregate existing and non-existing file-paths.

    Find all the valid files from the input argument and copy them to a
    destination location. Raises and handles(to log) invalid files.
    :Parameters:
        - cmd_line_arg : str : An element from
            ["dir1,file1[,file2...]", "dir2,file3[,file4...]", "file5"]
        - dest : str : Destination path to store the valid file(s).
        format sequence.
    """
    invalid = []
    cmd_line_arg = [i for i in cmd_line_arg.split(',') if i]
    path, files = cmd_line_arg[0], cmd_line_arg[1:]
    if os.path.isfile(path):
        path, base_name = os.path.split(path)
        files.append(base_name)
    if not os.path.isdir(path) or not len(files):
        invalid.append(path)
    for fil in set(files):
        fil_path = os.path.join(path, fil)
        if os.path.isfile(fil_path):
            shutil.copy(fil_path, dest)
        else:
            invalid.append(fil)
    try:
        raise InvalidArchFileError(
            'INVALID_FILES', (cmd_line_arg, ', '.join(invalid)))
    except DBPopulateError, e:
        print e


def extract_zip(zip_file, dest):
    """Extract ZIP file(s).

    Creates the directory tree for dest if not present.
    :Parameters:
        - zip_file : str : ZIP file path.
        - dest : str : Destination path to store the extracted file(s).
    :Raises:
        - BadZIPError if a ZIP file is invalid..
    """
    if not zipfile.is_zipfile(zip_file):
        raise BadZIPError('BAD_ZIP', zip_file)
    zip_obj = zipfile.ZipFile(zip_file)
    zip_obj.extractall(dest)


if __name__ == '__main__':
    pass
