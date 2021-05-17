#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" formatters.py
Description:
"""
__author__ = "Anthony Fong"
__copyright__ = "Copyright 2021, Anthony Fong"
__credits__ = ["Anthony Fong"]
__license__ = ""
__version__ = "0.2.0"
__maintainer__ = "Anthony Fong"
__email__ = ""
__status__ = "Beta"

# Default Libraries #
import logging
import datetime

# Downloaded Libraries #

# Local Libraries #


# Definitions #
# Classes #
class PreciseFormatter(logging.Formatter):
    """A logging Formatter that formats the time to the microsecond when a log occurs.

    Class Attributes:
        converter (:func:): The function the will convert the record to a datetime object.
        default_msec_format (str): The default string representation to use for milliseconds in a log.
    """
    converter = datetime.datetime.fromtimestamp
    default_msec_format = "%s.%06d"

    # Methods
    def formatTime(self, record, datefmt=None):
        """Return the creation time of the specified LogRecord as formatted text in milliseconds.

        Args:
            record: The log record.
            datefmt (str, optional): The format to use for milliseconds in the log.

        Returns:
            str: The string representation of milliseconds.
        """

        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime(self.default_time_format)
            s = self.default_msec_format % (t, ct.microsecond)
        return s
