#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Populate database with the event details.

GitHub time-line archives(*.json.gz) are the files that contain details
of user's events. These events are populated in the MongoDB database in
this module.

The module takes flagged input from the bash shell. The flags represent
the details of the archive and could be one of the followings:-

    1. URL for the Github archive(s).
    2. Date for the Github archive(s).
    3. Directory containing the archive(s).
    4. ZIP file of archive(s).
    5. Archive file(s).

For more on the flags, run the script with -h flag.
"""

import argparse
import glob
import gzip
import json
import os

from database import DBConfiguration
from errors import (DBPopulateError, ImproperArgsError, InvalidArchPathError,
                    NoArchiveFilesError,)
import gisc_msgs
from log import CLOG, FLOG
from utils import (download, empty_directory, extract_zip,
                   handle_valid_invalid_files, validate_date,)

__author__ = 'anshu.choubey@imaginea.com'


def check_if_params(ap_args):
    """Filter parameter(s) relevant to archive information.

    :Parameters:
        - ap_args : dict : Mapping of arguments and their values.
    :Raises:
        - ImproperArgsError if args doesn't have a valid argument on
        information about the archive.
    :Returns:
        - ap_args : dict : Relevant arguments and their values.
    """
    ap_args = {k: v for k, v in ap_args.iteritems()
               if k in gisc_msgs.VALID_ARGS}
    args_len = len(ap_args)
    if 'temp' in ap_args:
        args_len -= 1
    if 'delete_temp' in ap_args:
        args_len -= 1
    if args_len == 0:
        raise ImproperArgsError('NO_ARG', __file__)
    elif args_len > 1:
        raise ImproperArgsError('MULTIPLE_ARG', ', '.join(ap_args.keys()))
    return ap_args


def check_arg_for_none_value(ap_args):
    """Check if argument's values are finite.

    :Parameters:
        - ap_args : dict : Mapping of arguments and their values.
    :Raises:
        - ImproperArgsError if argument other than temp is of NoneType.
    """
    none_value_args = []
    for k, v in ap_args.iteritems():
        if k in ('temp', 'delete_temp'):
            continue
        if v is None or not len(v):
            none_value_args.append(k)
    if none_value_args:
        raise ImproperArgsError('NON_FINITE_ARGS', '',
                                ', '.join(none_value_args))


def get_url_from_date(arch_date):
    """Check if a URL is provided to download the archive(s).

    :Parameters:
        - arch_date : str : Date(range) of the archive(s).
    :Returns:
        - URL from the arch_date to download the archive.
    """
    arch_date = validate_date(arch_date)
    return gisc_msgs.URL_FORMAT % (arch_date,)


def populate(src_path, events_to_populate=gisc_msgs.POPULARITY_EVENTS):
    """Load the database with the event details.

    Creates a collection for every new event type and stores the event
    in it. Also stores the event in a collection for every event, i.e.
    AllEvent. This groups events by their type and also stores all of
    the events under one collection.
    :Parameters:
        - src_path : str : Directory path containing the archive(s).
        - events_to_populate : tuple : Type of events to be populated.
    :Raises:
        - InvalidArchPathError if directory path containing archive(s)
        doesn't exist.
        - NoArchiveFilesError if directory for archive(s) is empty.
    """
    decoder = json.JSONDecoder()
    if not os.path.isdir(src_path):
        raise InvalidArchPathError('DIR_PATH', src_path)
    gzs = glob.glob(os.path.join(src_path, '*.json.gz'))
    if not len(gzs):
        raise NoArchiveFilesError('EMPTY_DIR', src_path)

    db_obj = DBConfiguration(gisc_msgs.GISC_DB)
    all_coll = db_obj.coll(gisc_msgs.ALL_COLL)
    for i, gz in enumerate(gzs):
        with gzip.open(gz, 'rb') as fp:
            gz_data = fp.read()
            end, _events = 0, {}
            while end != len(gz_data):
                gz_event, end = decoder.raw_decode(gz_data, idx=end)
                event_type = gz_event['type']
                if event_type in events_to_populate:
                    entries = _events.get(event_type, [])
                    entries.append(gz_event)
                    _events[event_type] = entries
            for k, v in _events.iteritems():
                if not len(v):
                    continue
                db_obj.coll(k).insert(v)
                all_coll.insert(v)
        if (i + 1) % 10 == 0:
            CLOG.info('%d archives has been populated.' % (i + 1,))
    # W0631: Using possibly undefined loop variable
    # pylint: disable=W0631
    CLOG.info('Total archives populated :- %d' % (i + 1,))


def populate_events(ap_args):
    """Main function to populate the database with archive events.

    :Parameters:
        - ap_args : dict : Information related to archive(s).
    """
    FLOG.debug(ap_args)
    if __name__ != '__main__':
        ap_args = check_if_params(ap_args)
    check_arg_for_none_value(ap_args)
    CLOG.info('DB Populate args :- ' + str(ap_args))

    arch_path = ap_args.get('temp')
    del_arch_path = ap_args.get('delete_temp')
    if not arch_path:
        arch_path = gisc_msgs.TEMP_LOCATION
    arg = [k for k in ap_args if k is not 'temp'][0]

    if arg is 'url':
        empty_directory(arch_path)
        download(ap_args[arg], arch_path)
    elif arg is 'arch_date':
        empty_directory(arch_path)
        download(get_url_from_date(ap_args[arg]), arch_path)
    elif arg is 'src_dir':
        arch_path = ap_args[arg]
    elif arg is 'zip':
        extract_zip(ap_args[arg], arch_path)
    elif arg is 'files':
        empty_directory(arch_path)
        map(lambda x: handle_valid_invalid_files(x, arch_path), ap_args[arg])
    populate(arch_path)
    if arg is not 'src_dir' and del_arch_path:
        empty_directory(arch_path, False)


def setup_command_line_args_parse():
    """Setup the options for command line flags.

    :Returns:
        - ap : argparse.ArgumentParser object : Object with the options
        and their behaviour set.
    """
    _ap_args = dict(
        description=gisc_msgs.DB_USAGE_MSGS['description'],
        argument_default=argparse.SUPPRESS, add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    ap = argparse.ArgumentParser(**_ap_args)
    # Usage help argument.
    ap.add_argument('-h', '--help', action='help',
                    help=gisc_msgs.DB_USAGE_MSGS['help'])
    # Argument options.
    group = ap.add_mutually_exclusive_group(required=True)
#     # Archive URL.
#     group.add_argument('-u', nargs='?', dest='url',
#                        help=gisc_msgs.DB_USAGE_MSGS['url'])
#     # Archive date(range).
#     group.add_argument('-d', nargs='?', dest='arch_date',
#                        help=gisc_msgs.DB_USAGE_MSGS['arch_date'])
    # Archive directory.
    group.add_argument('-s', nargs='?', dest='src_dir',
                       help=gisc_msgs.DB_USAGE_MSGS['src_dir'])
    # Archive ZIP.
    group.add_argument('-z', nargs='?', dest='zip',
                       help=gisc_msgs.DB_USAGE_MSGS['zip'])
    # Archive file(s).
    group.add_argument('-f', nargs='*', dest='files',
                       help=gisc_msgs.DB_USAGE_MSGS['files'])
    # Temporary location argument.
    ap.add_argument('-t', nargs='?', dest='temp',
                    help=gisc_msgs.DB_USAGE_MSGS['temp'])
    # Delete temporary location.
    ap.add_argument('--delete_temp', action='store_true', default=False,
                    help=gisc_msgs.DB_USAGE_MSGS['delete_temp'])
    return ap


def get_ap_args(ap_obj, params=None):
    """Parse and get the command line arguments.

    :Parameters:
        - ap_obj : argparse.ArgumentParser object : Object with the
        options and their behaviour set.
        - params : list: Parameters to set options from. Used only in
        test cases. Hence, defaults to None.
    :Returns:
        - dict : Command line arguments.
    """
    # Group expected and garbage arguments.
    if params:
        ap_args, _ = ap_obj.parse_known_args(params)
    else:
        ap_args, _ = ap_obj.parse_known_args()
    return vars(ap_args)


if __name__ == '__main__':
    _args = get_ap_args(setup_command_line_args_parse())
    try:
        populate_events(_args)
    except DBPopulateError as e:
        CLOG.error(e)
