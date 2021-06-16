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
from multiprocessing import Event
from pickle import PickleError
from queue import Empty
import time
import warnings

# Downloaded Libraries #
from baseobjects import BaseObject, TimeoutWarning

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
    if not hasattr(handler, "__getstate__"):
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
    if not hasattr(handler, "__setstate__"):
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
        out_dict = self.__dict__.copy()
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
    """A modified FileHandler class which includes safe pickling."""

    # Magic Methods
    # Pickling
    def __getstate__(self):
        """Creates a dictionary of attributes which can be used to rebuild this object.

        Returns:
            dict: A dictionary of this object's attributes.
        """
        out_dict = super().__getstate__()
        if self.stream:
            self.close()
            out_dict["stream"] = True
        return out_dict

    def __setstate__(self, in_dict):
        """Builds this object based on a dictionary of corresponding attributes.

        Args:
            in_dict (dict): The attributes to build this object from.
        """
        super().__setstate__(in_dict)
        if in_dict["stream"]:
            self.stream = self._open()


class QueueHandler(logging.handlers.QueueHandler, PickableHandler):
    pass

# Todo: Create a SimpleQueueHandler with locked access to the send front end.


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

        async_loop: The event loop to assign the async methods to.
        _is_async (bool): Determines if this object will be asynchronous.
        alive_event (:obj:``Event): The Event that determines if alive.
        terminate_event (:obj:`Event`): The Event used to stop the task loop.

    Args:
        queue (:obj:`Queue`): The queue to get the LogRecords from.
        *handlers (:obj:`Handler`): The handlers to handle the incoming LogRecords.
        respect_handler_level (bool): Determines if this object will check the level of each message to the handler’s.
    """

    # Construction/Destruction
    def __init__(self, queue, *handlers, respect_handler_level=False):
        super().__init__(queue, *handlers, respect_handler_level=respect_handler_level)
        self.async_loop = asyncio.get_event_loop()
        self._is_async = True
        self.alive_event = Event()
        self.terminate_event = Event()

    @property
    def is_async(self):
        """bool: If this object is asynchronous. It will detect if it asynchronous while running.

        When set it will raise an error if the Task is running.
        """
        if self.is_alive():
            if self._thread is not None:
                return False
            else:
                return True
        else:
            return self._is_async

    @is_async.setter
    def is_async(self, value):
        self._is_async = value
        if self.is_alive():
            raise ValueError("cannot set is_async while LogListener is running.")

    # Pickling
    def __getstate__(self):
        """Creates a dictionary of attributes which can be used to rebuild this object

        Returns:
            dict: A dictionary of this object's attributes.
        """
        if self.is_alive():
            raise PickleError("Cannot pickle while alive")
        out_dict = self.__dict__.copy()
        out_dict["safe_handlers"] = pickle_safe_handlers(self.handlers)
        del out_dict["async_loop"], out_dict["handlers"]
        return out_dict

    def __setstate__(self, in_dict):
        """Builds this object based on a dictionary of corresponding attributes.

        Args:
            in_dict (dict): The attributes to build this object from.
        """
        in_dict["handlers"] = unpickle_safe_handlers(in_dict.pop("safe_handlers"))
        in_dict["async_loop"] = asyncio.get_event_loop()
        self.__dict__ = in_dict

    # Methods
    # State
    def is_alive(self):
        """Checks if this object is currently running.

        Returns:
            bool: If this object is currently running.
        """
        return self.alive_event.is_set()

    # Listening
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

    def _monitor(self):
        """
        Monitor the queue for records, and ask the handler
        to deal with them.

        This method runs on a separate, internal thread.
        The thread will terminate if it sees a sentinel object in the queue.
        """
        q = self.queue
        has_task_done = hasattr(q, 'task_done')

        while not self.terminate_event.is_set():
            try:
                record = self.dequeue(True)
                if record is self._sentinel:
                    if has_task_done:
                        q.task_done()
                    break
                self.handle(record)
                if has_task_done:
                    q.task_done()
            except Empty:
                break

        self.alive_event.clear()

    async def _monitor_async(self):
        """Asynchronously monitor the queue for records and ask the handler to deal with them."""
        q = self.queue
        has_task_done = hasattr(q, 'task_done')

        while not self.terminate_event.is_set():
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

        self.alive_event.clear()

    # Joins
    def join_normal(self, timeout=None):
        """Wait until this object terminates and determines if the async version should be run.

        Args:
            timeout (float): The time in seconds to wait for termination.
        """
        if self.is_async:
            start_time = time.perf_counter()
            while self.alive_event.is_set():
                if timeout is not None and (time.perf_counter() - start_time) >= timeout:
                    warnings.warn(TimeoutWarning("'join_normal'"), stacklevel=2)
                    return
        else:
            self._thread.join(timeout)

    async def join_async(self, timeout=None, interval=0.0):
        """Asynchronously wait until this object terminates.

        Args:
            timeout (float): The time in seconds to wait for termination.
            interval (float): The time in seconds between termination checks. Zero means it will check ASAP.
        """
        if self.is_async:
            start_time = time.perf_counter()
            while self.alive_event.is_set():
                await asyncio.sleep(interval)
                if timeout is not None and (time.perf_counter() - start_time) >= timeout:
                    warnings.warn(TimeoutWarning("'join_async'"), stacklevel=2)
                    return
        else:
            self._thread.join(timeout)

    def join_async_task(self, timeout=None, interval=0.0):
        """Creates waiting for this object to terminate as an asyncio task.

        Args:
            timeout (float): The time in seconds to wait for termination.
            interval (float): The time in seconds between termination checks. Zero means it will check ASAP.
        """
        return asyncio.create_task(self.join_async(timeout, interval))

    def join(self, asyn=False, timeout=None, interval=0.0):
        """Wait until this object terminates and determines if the async version should be run.

        Args:
            asyn (bool): Determines if the join will be asynchronous.
            timeout (float): The time in seconds to wait for termination.
            interval (float): The time in seconds between termination checks. Zero means it will check ASAP.
        """
        # Use Correct Context
        if asyn:
            return self.join_async_task(timeout, interval)
        else:
            self.join_normal(timeout)
            return None

    # Execution
    def start(self):
        """Start the listener as either a thread or async loop."""
        if self.is_alive():
            raise RuntimeError("LogListener is already running.")

        self.alive_event.set()

        if not self.is_async:
            super().start()
        else:
            asyncio.run(self._monitor_async())

    def start_async_task(self):
        """Creates the continuous execution of the listener as an asyncio task."""
        if self.is_alive():
            raise RuntimeError("LogListener is already running.")

        self._is_async = True
        self.alive_event.set()

        return asyncio.create_task(self._monitor_async())

    def stop(self, join=True, asyn=False, timeout=None, interval=0.0):
        """Stop the listener.

        Args:
            join (bool): Determines if terminate will wait for the object to join.
            asyn (bool): Determines if the join will be asynchronous.
            timeout (float): The time in seconds to wait for termination.
            interval (float): The time in seconds between termination checks. Zero means it will check ASAP.

        Returns:
            Can return None or an async_io task object if this function is called with async on.
        """
        self.enqueue_sentinel()
        if join:
            self.join(asyn, timeout, interval)

    def terminate(self, join=False, asyn=False, timeout=None, interval=0.0):
        """Flags the task loop and task to stop running.

        Args:
            join (bool): Determines if terminate will wait for the object to join.
            asyn (bool): Determines if the join will be asynchronous.
            timeout (float): The time in seconds to wait for termination.
            interval (float): The time in seconds between termination checks. Zero means it will check ASAP.

        Returns:
            Can return None or an async_io task object if this function is called with async on.
        """
        self.terminate_event.set()
        if join:
            return self.join(asyn, timeout, interval)
