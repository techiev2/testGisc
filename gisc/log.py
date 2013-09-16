#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Logging module for GISC operations.

Initialises the "console" and "file" loggers. Sets "file" logger's
handler when the directory path or log file has been input by user.
"""

import logging.config
import os
import sys

from confs.custom_handler import TRFileHandler

__author__ = "anshu.choubey@imaginea.com"

logging.raiseExceptions = True
curr_dir = os.path.dirname(os.path.realpath(__file__))
CONFIG = os.path.join(curr_dir, 'confs/log.ini')

sys.path.append(os.path.dirname(CONFIG))

logging.config.fileConfig(CONFIG)
CLOG = logging.getLogger('clog')
FLOG = logging.getLogger('flog')


def set_logs_dir(logs_dir=None):
    """Sets logging directory path.

    Removes the "file" logger handler existence and adds a new handler
    initialised with the desired log directory path.
    :Parameters:
        - logs_dir : str : Path where log file is to be generated.
    """
    if not logs_dir:
        return
    hdlr = FLOG.handlers[0]
    base_file = os.path.basename(hdlr.baseFilename)
    FLOG.removeHandler(hdlr)
    hdlr = TRFileHandler(base_file, logs_dir)
    FLOG.addHandler(hdlr)
