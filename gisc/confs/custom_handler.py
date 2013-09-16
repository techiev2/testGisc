#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Customise handler for file logging.

Used while dynamically setting the directory for log path.
"""

import os

from logging.handlers import TimedRotatingFileHandler

__author__ = "anshu.choubey@imaginea.com"

curr_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(curr_dir)
LOGS_DIR = os.path.join(parent_dir, 'logs')


class TRFileHandler(TimedRotatingFileHandler):
    def __init__(self, file_name, logs_dir=None):
        if not logs_dir:
            logs_dir = LOGS_DIR
        if not os.path.isdir(logs_dir):
            os.makedirs(logs_dir)
        super(TRFileHandler, self).__init__(os.path.join(logs_dir, file_name))
