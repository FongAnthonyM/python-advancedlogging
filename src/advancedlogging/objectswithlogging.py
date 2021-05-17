#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" objectswithlogging.py

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
import abc
import copy

# Downloaded Libraries #

# Local Libraries #


# Definitions #
# Classes #
class ObjectWithLogging(abc.ABC):
    """Class that has inbuilt logging as an option.

    Loggers can be defined on the class level or object level and be shared to other namespaces. Class loggers can be
    defined in the class_loggers attribute, additionally class loggers can be defined in the build_class_loggers class
    method. These class loggers are present in all objects of this class, so any object can use these loggers which
    is good for seeing what all objects of a class are doing. Object loggers are defined in the build_loggers method.
    Any loggers added here are only available to the object executing this method. This is useful for creating a private
    logger exclusive to a specific object.

    Class Attributes:
        class_loggers (dict): The default loggers to include in every object of this class.

    Attributes:
        loggers (dict): A collection of loggers used by this object. The keys are the names of the different loggers.
        name (str): The name of this object.
    """
    class_loggers = {}

    # Class Methods
    @classmethod
    def build_class_loggers(cls):
        """Setup class loggers here"""
        pass

    # Construction/Destruction
    def __init__(self):
        self.loggers = self.class_loggers.copy()
        self.name = ""

    def __copy__(self):
        """The copy magic method (shallow)

        Returns:
            :obj:`ObjectWithLogging`: A shallow copy of this object.
        """
        new = type(self)()
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo={}):
        """Overrides the deep copy magic method to ensure the dynamically inheriting objects are copied.

        Args:
            memo (dict): A dictionary of user defined information to pass to another deepcopy call which it will handle.

        Returns:
            :obj:`ObjectWithLogging`: A deep copy of this object.
        """
        new_dict = {}
        new = type(self)()
        for k, i in self.__dict__.items():
            new_dict[k] = copy.deepcopy(i)
        new.__dict__.update(self.__dict__)
        return new

    # Methods
    # Logging
    def build_loggers(self):
        """Setup object loggers here"""
        pass

    def update_loggers(self, loggers=None):
        """Updates the loggers to add more from either a dictionary or the class loggers.

        Args:
            loggers (dict, optional): The dictionary of loggers to add to this object. If None then updates from class.

        Returns:
            dict: This object's loggers
        """
        if loggers is None:
            loggers = self.class_loggers
        self.loggers.update(loggers)
        return self.loggers

    def trace_log(self, logger, func, msg, *args, name=None, level="DEBUG", append=None, **kwargs):
        """Creates a trace log for a given logger.

        Args:
            logger (str): The name of logger to log to.
            func (str): The name of function/method this log is being made from.
            msg (str): The name of class this log is being made from.
            *args: The arguments for the original log method.
            name (str, optional): The an additional identifier that can be used to trace this log.
            level (str or int, optional): The level to create log entry for.
            append (bool, optional): Determines if append message should be added. Defaults to attribute if left None.
            **kwargs: The key word arguments for the original log method.
        """
        if name is None:
            name = self.name
        self.loggers[logger].trace_log(type(self), func, msg, *args, name=name, level=level, append=append, **kwargs)
