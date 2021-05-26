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
import asyncio
import copy
import logging
from logging import Handler
import logging.handlers
from logging.handlers import QueueListener
from queue import Empty
import time
import warnings

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
    if hasattr(handler, "__getstate__"):
        new_handler = copy.copy(handler)
        new_handler.lock = None
        if "stream" in new_handler.__dict__:
            new_handler.stream = None
            if not isinstance(new_handler, logging.FileHandler):
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
    if hasattr(handler, "__setstate__"):
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
# Warnings #
class TimeoutWarning(Warning):
    """A general warning for timeouts."""
    def __init__(self, name="A function"):
        message = f"{name} timed out"
        super().__init__(message)


# Handlers
class PickableHandler(BaseObject, Handler):
    """An abstract handler that implements safe pickling for a handler."""

    # Magic Methods
    # Pickling
    def __getstate__(self):
        """Creates a dictionary of attributes which can be used to rebuild this object.

        Returns:
            dict: A dictionary of this object's attributes.
        """
        out_dict = copy.copy(self.__dict__)
        out_dict.pop("lock")
        return out_dict

    def __setstate__(self, in_dict):
        """Builds this object based on a dictionary of corresponding attributes.

        Args:
            in_dict (dict): The attributes to build this object from.
        """
        self.__dict__ = in_dict
        self.createLock()


class FileHandler(logging.FileHandler, PickableHandler):
    pass


class QueueHandler(logging.handlers.QueueHandler, PickableHandler):
    pass

# Todo: Create an h5 handler


# Listeners
class LogListener(BaseObject, QueueListener):
    """An internal threaded listener which watches for LogRecords being added to a queue and processes them.

    Class Attributes:
        _sentinel: The object added to the queue to stop the thread running the listener.

    Attributes:
        queue (:obj:`Queue`): The queue to get the LogRecords from.
        handlers: The handlers to handle the incoming LogRecords.
        _thread: The thread which the listener is running on.
        respect_handler_level (bool): Determines if this object will check the level of each message to the handler’s.

    Args:
        queue (:obj:`Queue`): The queue to get the LogRecords from.
        *handlers (:obj:`Handler`): The handlers to handle the incoming LogRecords.
        respect_handler_level (bool): Determines if this object will check the level of each message to the handler’s.
    """

    # Methods
    async def dequeue_async(self, timeout=None, interval=0.0):
        """Asynchronously, get an item from the queue.

        Args:
            timeout (float, optional): The time in seconds to wait for an item from the queue before exiting.
            interval (float, optional): The time in seconds between each queue query.

        Returns:
            An object from the queue.
        """
        # Track time for timeout
        start_time = time.perf_counter()

        # Query queue for item and check at every interval
        while self.queue.empty():
            await asyncio.sleep(interval)
            if timeout is not None and (time.perf_counter() - start_time) >= timeout:
                warnings.warn(TimeoutWarning("'dequeue_async'"), stacklevel=2)
                return None

        return self.queue.get()

    async def _monitor_async(self):
        """Asynchronously monitor the queue for records and ask the handler to deal with them."""
        q = self.queue
        has_task_done = hasattr(q, 'task_done')
        while True:
            try:
                record = await self.dequeue_async()
                if record is self._sentinel:
                    if has_task_done:
                        q.task_done()
                    break
                self.handle(record)
                if has_task_done:
                    q.task_done()
            except Empty:
                break

