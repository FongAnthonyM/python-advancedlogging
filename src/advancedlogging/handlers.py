#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" handlers.py
Description:
"""
__author__ = "Anthony Fong"
__copyright__ = "Copyright 2021, Anthony Fong"
__credits__ = ["Anthony Fong"]
__license__ = ""
__version__ = "0.2.0"
__maintainer__ = "Anthony Fong"
__email__ = ""
__status__ = "Prototype"

# Default Libraries #
import copy
import logging
import warnings
from logging import Handler, FileHandler
import logging.handlers


# Downloaded Libraries #
from baseobjects import BaseObject

# Local Libraries #


# Definitions #
# Functions #
def pickle_safe_handler(handler):
    """Creates a logging handler that is safe to pickle.

    Args:
        handler (:obj:`Handler`): A handler to make a picklable version of.

    Returns:
        :obj:`Handler`: A handler that can be pickled.
    """
    if "__getstate__" not in set(dir(type(handler))):
        new_handler = copy.copy(handler)
        new_handler.lock = None
        if "stream" in new_handler.__dict__:
            new_handler.stream = None
            if not isinstance(new_handler, FileHandler):
                warnings.warn(f"A {type(new_handler)} was pickled but the stream was removed.")
        return new_handler
    else:
        return handler


def pickle_safe_handlers(handlers):
    """Creates logging handlers that are safe to pickle.

    Args:
        handlers (:obj:`list` of :obj:`Handler`): Handlers to make a picklable version.

    Returns:
        :obj:`list` of :obj:`Handler`: Handlers that can be pickled.
    """
    new_handlers = []
    for handler in handlers:
        new_handlers.append(pickle_safe_handler(handler))
    return new_handlers


def unpickle_safe_handler(handler):
    """Return a pickle safe handler back to a normal logging handler.

    Args:
        handler (:obj:`Handler`): A pickle safe handler to turn into a normal logging handler.

    Returns:
        :obj:`Handler`: A normal logging handler that was pickled.
    """
    if "__setstate__" not in set(dir(type(handler))):
        handler.createLock()
    return handler


def unpickle_safe_handlers(handlers):
    """Returns pickle safe handlers back to normal logging handlers.

    Args:
        handlers (:obj:`list` of :obj:`Handler`): Pickle safe handlers to turn into normal logging handlers.

    Returns:
        :obj:`list` of :obj:`Handler`: A logging handlers that were pickled.
    """
    new_handlers = []
    for handler in handlers:
        new_handlers.append(unpickle_safe_handler(handler))
    return new_handlers


# Classes #
class PickableHandler(BaseObject, Handler):
    # Pickling
    def __getstate__(self):
        """Creates a dictionary of attributes which can be used to rebuild this object.

        Returns:
            dict: A dictionary of this object's attributes.
        """
        out_dict = copy.deepcopy(self.__dict__)
        out_dict.pop("lock")
        return out_dict

    def __setstate__(self, in_dict):
        """Builds this object based on a dictionary of corresponding attributes.

        Args:
            in_dict (dict): The attributes to build this object from.
        """
        self.__dict__ = in_dict
        self.createLock()

# Todo: Create an h5 handler

