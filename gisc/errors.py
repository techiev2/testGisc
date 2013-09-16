#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""GISC Exceptions module."""

from gisc_msgs import ERROR_CODE_MSGS
from log import FLOG

__author__ = "anshu.choubey@imaginea.com"


class GISCError(Exception):
    """GISC error base class."""
    def __init__(self, code, formats=None, exc_msg=None):
        try:
            msg = ERROR_CODE_MSGS[code]
        except KeyError:
            # @todo: Implement logging here.
            msg = ERROR_CODE_MSGS['UNIMPLEMENTED_CODE']
            formats = (code, exc_msg)
            msg = msg % formats
        else:
            try:
                if formats:
                    msg = msg % formats
            except TypeError as err:
                # @todo: Implement logging here.
                msg = ERROR_CODE_MSGS['IMPROPER_FORMATTING']
                formats = (code, err, exc_msg)
                msg = msg % formats
        finally:
            FLOG.error(msg)
        super(GISCError, self).__init__(msg)


class DBPopulateError(GISCError):
    """Populating database error."""


class BadZIPError(DBPopulateError):
    """Bad or corrupt ZIP for archive(s) error."""


class ImproperArgsError(DBPopulateError):
    """Improper args about archive information error."""


class InvalidArchFileError(DBPopulateError):
    """Invalid archive file name to copy error."""


class InvalidArchPathError(DBPopulateError):
    """Invalid directory path for archive error."""


class NoArchiveFilesError(DBPopulateError):
    """No *.json.gz file in directory path for archive error."""


class DefaultArgInvalidValError(GISCError):
    """Default argument over-ridden by invalid value(None) error."""


class DBConfigurationError(GISCError):
    """Database configuration error."""


class DBCollNameError(DBConfigurationError):
    """Database or collection name invalid type error."""


class InvalidLanguageError(GISCError):
    """Querying an unknown language error."""


class UnexpectedDateTimeStampError(GISCError):
    """Unexpected date time stamp format to parse error."""
