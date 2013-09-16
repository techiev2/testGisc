#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Define the hard-coded messages, their mapping or the variables."""

__author__ = "anshu.choubey@imaginea.com"

# Database.
GISC_DB = 'gisc'
# Collections.
ALL_COLL = 'AllEvent'
FOLLOW_COLL = 'FollowEvent'
WATCH_COLL = 'WatchEvent'
# Database configuration statement.
DB_CONFIG_STMNT = 'Configured database :- %s'
# Archive populate statement:
ARCH_POPULATE_STMNT = '%d archives have been populated.'
# Default temporary location to store *.gz JSON files.
TEMP_LOCATION = '/tmp/gisc_jsons'
# Events related to popularity of a repository.
POPULARITY_EVENTS = ('PushEvent', 'WatchEvent', 'FollowEvent')
# Valid argument names.
VALID_ARGS = ('url', 'arch_date', 'src_dir', 'zip', 'files', 'temp')
# URL format for date argument.
URL_FORMAT = 'http://data.githubarchive.org/%s.json.gz'
# Date format.
DATE_FMT = 'Enter date in yyyy-mm-dd-h[h] format.'

# Default format for image file to be plotted.
IMG_FMT = 'png'
# Default location to store the plot files.
PLOT_LOCATION = '/tmp/plots'
# No watch event for user debug template.
NO_WATCH_DEBUG = 'No watch event found for user :- %s'
# populate_db.py usage.
#######################
# Argparse description.
_POPULATE_DB_DESC = '\n'.join([
    'Loads event JSONs from GitHub time-line archive into the database.',
    'Event JSONs could be one from new commits, fork events, to opening',
    'new tickets, commenting, and adding members to a project. The event',
    'activities are aggregated in hourly archives.',
    'For details on events, visit http://www.githubarchive.org/'])
# Usage help text.
_USAGE_HELP = 'Show this help message.'
# URL argument help text.
_URL_HELP = '\n'.join([
    'URL to the GitHub time-line archive.',
    'e.g: http://data.githubarchive.org/2012-04-{05..25}-{2..18}.json.gz',
    'for 2 hrs to 18 hrs from date 5 to 25 of the April month of 2012.'])
# Date argument help text.
_DATE_HELP = '\n'.join([
    'Target date in the format yyyy-mm-dd-h[h].',
    'Every of yyyy, mm, dd, h[h] could be a range in the form of',
    '{$START$..$END$} or in the form {$START$,$END$}, where,',
    '$START$ and $END$ are start and end of the range respectively.',
    'h[h] in range 0-9 must be single digit.',
    'If a range is used, the braces are escaped using "\" before them.',
    'e.g: 2012-04-\{05..25\}-\{12..18\} implies, events activity for',
    '12 hrs to 18 hrs from date 5 to 25 of the April month of 2012.',
    'Multiple range values not supported as of yet.',
    'e.g: 2012-04-\{05..15,20..25\}-\{00..06,12..18\} won\'t work.'])
# Other possible argument help text.
_SRC_HELP = 'Directory path of the *.gz file(s).'
_ZIP_HELP = 'ZIP path(s) of the *.gz file(s).'
_FILES_HELP = '\n'.join([
    'Path(s) of the *.gz file(s) or comma-separated file names starting',
    'with the directory containing them.',
    'e.g: full_path1 [full_path2 [full_path3...]] or,',
    '     dir1,file1[,file2...] [dir2,file3[,file4...]] and so on.',
    'where dir1 is the path containing the files file1, file2.'])
# Temporary location help text.
_TEMP_HELP = '\n'.join([
    'Path to store the *.gz file(s) for processing in case of URL or ZIP',
    'or date file being the input. Not evaluated in case of source being',
    'directory of *.gz file(s).',
    'Note :- Directory if exists is deleted and created from scratch.'
    'Defaults to location :- %s' % TEMP_LOCATION])
_DEL_HELP = '\n'.join([
    'Include this flag to delete the temporary location after processing.',
    'Note :- Not evaluated when source is a directory of *.gz file(s).'])
# Argparse helpers and description mapping for populating database usage.
DB_USAGE_MSGS = {'description': _POPULATE_DB_DESC, 'help': _USAGE_HELP,
                 'url': _URL_HELP, 'arch_date': _DATE_HELP,
                 'src_dir': _SRC_HELP, 'zip': _ZIP_HELP,
                 'files': _FILES_HELP, 'temp': _TEMP_HELP,
                 'delete_temp': _DEL_HELP,
                 }

# gisc.py usage.
#######################
# Argparse description.
_GISC_DESC = '\n'.join([
    'APIs to manipulate user dynamics and events co-relations by querying',
    'database and producing their plots to understand the trends followed',
    'by other users for repositories and miscellaneous details.'])
# Repository language to manipulate results on help text.
_LANG_HELP = 'Case-insensitive repository language to get results for.'
# Count of objects to be considered for the analysis help text.
_COUNT_HELP = '\n'.join([
    'Number of objects to be considered for the analysis. Not to be used',
    'when all entries are supposed to be considered.'])
# Image file extension to be used.
_IMG_FMT_HELP = '\n'.join([
    'Extension format for the image file without period at the beginning.',
    'e.g: jpg, jpeg.',
    'Defaults to format :- %s' % IMG_FMT])
# Plot path help text.
_PLOT_HELP = '\n'.join([
    'Directory path to store the graphs or the plots.',
    'Note :- Directory if exists is deleted and created from scratch.'
    'Defaults to location :- %s' % PLOT_LOCATION])
# Log path help text.
_LOGS_HELP = '\n'.join([
    'Directory path to store the log file. By default, log is stored in the',
    'logs directory inside the "gisc" project.'])
# Argparse helpers and description mapping for GISC APIs usage.
GISC_USAGE_MSGS = {'description': _GISC_DESC, 'help': _USAGE_HELP,
                   'lang': _LANG_HELP, 'count': _COUNT_HELP,
                   'plot_dir': _PLOT_HELP, 'logs_dir': _LOGS_HELP,
                   'img_fmt': _IMG_FMT_HELP,
                   }

# Error messages:
#################
# No argument.
_NO_ARG = '\n'.join(['Archive parameter missing.',
                     'Render one of the following details for archive :-',
                     ', '.join(VALID_ARGS), '',
                     'For more on above parameters, execute following from',
                     'the bash shell:', 'python %s -h'])
# Multiple arguments.
_MULTIPLE_ARG = '\n'.join(['Too many archive parameters found.',
                           'Render only one of these parameters :-', '%s'])
# Argument values not entered.
_NON_FINITE_ARGS = '\n'.join(['Enter argument values for following params :-',
                             '%s'])

# @todo: Re-write date related functions and error messages.
_MISSING_VALUE = '\n'.join(['Doesn\'t match expected format :- %s',
                            DATE_FMT, ''])
_IMPROPER_VALUE = '\n'.join([
    'Value for %s(%s bound, if range) is improper in :- %s', DATE_FMT, ''])
_IMPROPER_TYPE = '\n'.join(['Date figures are to be integers in :- %s',
                            DATE_FMT, ''])
_OUT_BRACKET = 'Date(range) entered is not between February 12, 2011 & today.'

# Missing archive directory path.
_DIR_PATH = '\n'.join(['Archive directory path not found :-', '%s'])
# Empty archive directory.
_EMPTY_DIR = '\n'.join(['Archive directory path is empty :-', '%s'])
# Corrupt or invalid ZIP file.
_BAD_ZIP = '\n'.join(['Invalid or corrupt ZIP file :-', '%s'])
# Non-existing archive file names to copy.
_INVALID_FILES = '\n'.join(['In the given cluster of files to process :- %s',
                            'Following file names don\'t exist :- %s'])
# Invalid type for database or collection name.
_INVALID_TYPE = 'Name must be an instance of BaseString :- %s'
# Default argument being None.
_INVALID_DEFAULT_ARG = 'Default argument can\'t be left empty :- %s'
# Unknown repository language being filtered on.
_INVALID_LANG = 'Unknown repository language: %s'
# Unhandled datetime format to parse.
_UNEXPECTED_DTSTAMP = '\n'.join([
    'The dataetime doesn\'t match the expected format :- %s'])
_UNIMPLEMENTED_CODE = '\n'.join(['Error code not implemented :- %s',
                                 'Original error :- %s'])
_IMPROPER_FORMATTING = '\n'.join([
    'Error while string formating for the code :- %s',
    'Formatting error :- %s', 'Original error :- %s'])

# Error messages mapping.
ERROR_CODE_MSGS = {
    'NO_ARG': _NO_ARG, 'MULTIPLE_ARG': _MULTIPLE_ARG,
    'NON_FINITE_ARGS': _NON_FINITE_ARGS, 'DIR_PATH': _DIR_PATH,
    'EMPTY_DIR': _EMPTY_DIR, 'BAD_ZIP': _BAD_ZIP,
    'INVALID_FILES': _INVALID_FILES, 'INVALID_TYPE': _INVALID_TYPE,
    'INVALID_DEFAULT_ARG': _INVALID_DEFAULT_ARG, 'INVALID_LANG': _INVALID_LANG,
    'UNEXPECTED_DTSTAMP': _UNEXPECTED_DTSTAMP,
#     'MISSING_VALUE': _MISSING_VALUE, 'IMPROPER_TYPE': _IMPROPER_TYPE,
#     'IMPROPER_VALUE': _IMPROPER_VALUE, 'OUT_BRACKET': _OUT_BRACKET,
    'UNIMPLEMENTED_CODE': _UNIMPLEMENTED_CODE,
    'IMPROPER_FORMATTING': _IMPROPER_FORMATTING,
}
