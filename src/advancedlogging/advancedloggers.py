#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" advancedlogging.py

"""
__author__ = "Anthony Fong"
__copyright__ = "Copyright 2020, Anthony Fong"
__credits__ = ["Anthony Fong"]
__license__ = ""
__version__ = "0.2.0"
__maintainer__ = "Anthony Fong"
__email__ = ""
__status__ = "Beta"

# Default Libraries #
import copy
import logging
import logging.config
import statistics
import time
import warnings

# Downloaded Libraries #
from baseobjects import StaticWrapper

# Local Libraries #
from .formatters import PreciseFormatter
from .handlers import pickle_safe_handlers, unpickle_safe_handlers


# Definitions #
# Classes #
class AdvancedLogger(StaticWrapper):
    """A logger with expanded functionality that wraps a normal logger.

    Class Attributes:
        _attributes_as_parents (:obj:'list' of :obj:'str'): The list of attribute names that will contain the objects to
            dynamically wrap where the order is descending inheritance. In this case a logger will be dynamically
            wrapped.
        default_levels (dict): The default logging levels with their names mapped to their numerical values.

    Attributes:
        name (str): The name of this logger.
        level (int): The logging level of this logger.
        parent (str): The parent logger of this logger.
        propagate (bool): Determines if a log will be sent to the parent logger.
        handlers (list): The handlers for this logger.
        disabled (bool): Determines if this logger will log.

        quick_check (bool): Determines if a check quick should be done instead of a full level check.
        levels (dict): The logging levels with their names mapped to their numerical values.
        module_of_class (str): The name of module the class originates from.
        module_of_object (str): The name of the module this object originates from.
        allow_append (bool): Allows an additional message to be appended to all logs.
        append_message (str): A message to append to all logs.

    Args:
        obj: The logger that this object will wrap or the name of the logger to create.
        module_of_class (str, optional): The name of module the class originates from.
        init (bool, optional): Determines if this object should be initialized.
    """
    _wrapped_types = [logging.getLogger()]
    _wrap_attributes = ["_logger"]
    default_levels = {"DEBUG": logging.DEBUG,
                      "INFO": logging.INFO,
                      "WARNING": logging.WARNING,
                      "ERROR": logging.ERROR,
                      "CRITICAL": logging.CRITICAL}

    @classmethod
    def from_config(cls, name, fname, defaults=None, disable_existing_loggers=True, **kwargs):
        """Loads the logger's configuration from a file.

        Args:
            name (str): The name of the logger.
            fname (str): The file path of the config file.
            defaults: Additional configurations to set.
            disable_existing_loggers (bool): Disables current active loggers.
            **kwargs: Passes addition keyword arguments to AdvancedLogger initialization.

        Returns:
            AdvancedLogger: A logger with the loaded configurations.
        """
        logging.config.fileConfig(fname, defaults, disable_existing_loggers)
        return cls(name, **kwargs)

    # Construction/Destruction
    def __init__(self, obj=None, module_of_class="(Not Given)", init=True):
        self._logger = None

        self.quick_check = False
        self.levels = self.default_levels.copy()
        self.module_of_class = "(Not Given)"
        self.module_of_object = "(Not Given)"
        self.allow_append = False
        self.append_message = ""

        if init:
            self.construct(obj, module_of_class)

    @property
    def name_parent(self):
        """str: The names encapsulating parents of this logger."""
        return self._logger.name.rsplit('.', 1)[0]

    @property
    def name_stem(self):
        """str: The names encapsulating parents of this logger."""
        return self._logger.name.rsplit('.', 1)[-1]

    # Pickling
    def __getstate__(self):
        """Creates a dictionary of attributes which can be used to rebuild this object

        Returns:
            dict: A dictionary of this object's attributes.
        """
        out_dict = copy.deepcopy(self.__dict__)
        out_dict["handlers"] = pickle_safe_handlers(self._logger.handlers)
        del out_dict["_logger"].handlers
        return out_dict

    def __setstate__(self, in_dict):
        """Builds this object based on a dictionary of corresponding attributes.

        Args:
            in_dict (dict): The attributes to build this object from.
        """
        in_dict["_logger"].handlers = unpickle_safe_handlers(in_dict.pop("handlers"))
        self.__dict__ = in_dict

    # Methods
    # Constructors/Destructors
    def construct(self, obj=None, module_of_class="(Not Given)"):
        """Constructs this object.

        Args:
            obj: The logger that this object will wrap or the name of the logger to create.
            module_of_class (str): The name of the module of the class this logger originates from.
        """
        self.module_of_class = module_of_class
        if isinstance(obj, logging.Logger):
            self._logger = obj
        else:
            self._logger = logging.getLogger(obj)

    # State
    def isEnabledFor(self, level):
        """Checks if a supplied level is enabled for this logger.

        Args:
            level: The level to check if it is enabled for this logger.

        Returns:
            bool: If the level is endabled for this logger.
        """
        if self._logger.disabled:
            return False

        if isinstance(level, str):
            return self.levels[level] >= self._logger.level
        else:
            return level >= self._logger.level

    # Levels Methods
    def get_level(self, name):
        """Gets the level value based on the name within the levels dictionary.

        Args:
            name (str): The name of the level to get the value of.

        Returns:
            int: The numerical value of the level.
        """
        if isinstance(name, str):
            return self.levels[name]
        else:
            return name

    # Base Logger Editing
    def set_base_logger(self, logger):
        """Set the logger which this object wraps.

        Args:
            logger (:obj:`Logger`, optional): The logger that this object will wrap.
        """
        self._logger = logger

    def fileConfig(self, name, fname, defaults=None, disable_existing_loggers=True):
        """Set the logger's configuration base on a file

        Args:
            name (str): The name of the logger.
            fname (str): The file path of the config file.
            defaults: Additional configurations to set.
            disable_existing_loggers (bool): Disables current active loggers.
        """
        logging.config.fileConfig(fname, defaults, disable_existing_loggers)
        self._logger = logging.getLogger(name)

    def copy_logger_attributes(self, logger):
        """Copies this loggers attributes to another logger.

        Args:
            logger: The logger to copy this loggers attributes to.

        Returns:
            logger: The logger which the attributes were copied to.
        """
        logger.propagate = self._logger.propagate
        logger.setLevel(self._logger.getEffectiveLevel())
        for filter_ in self._logger.filters:
            logger.addFilter(filter_)
        for handler in self._logger.handlers:
            logger.addHandler(handler)
        return logger

    def getChild(self, name, **kwargs):
        """Create a child logger of this logger which will be an AdvancedLogger or one its subclasses.

        Args:
            name: The name of the new logger.
            **kwargs: The other key word arguments used to make a new logger.
        """
        new_logger = self._logger.getChild(name)
        return type(self)(new_logger, **kwargs)

    def setParent(self, parent):
        """Change this logger to be a child under another logger.

        Args:
            parent: The logger to become a child under.
        """
        new_logger = parent.getChild(self.name_stem)
        if isinstance(new_logger, AdvancedLogger):
            new_logger = new_logger._logger
        self.copy_logger_attributes(new_logger)
        self._logger = new_logger

    # Defaults
    def append_module_info(self):
        """Sets the append message to bet the module information"""
        self.append_message = "Class' Module: %s Object Module: %s " % (self.module_of_class, self.module_of_object)
        self.allow_append = True

    def add_default_stream_handler(self, stream=None, level="DEBUG"):
        """Adds a stream handler with Debug level output and a formatter that millisecond precise time.

        Args:
            stream: The stream to send the logs to.
            level (str or int, optional): The level which the logger will start logging.
        """
        if isinstance(level, str):
            level = self.get_level(level)
        handler = logging.StreamHandler(stream=stream)
        handler.setLevel(level)
        formatter = PreciseFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def add_default_file_handler(self, filename, mode='a', encoding=None, delay=False, level="DEBUG"):
        """Adds a file handler with Debug level output and a formatter that millisecond precise time.

        Args:
            filename: The path to the output file for the log.
            mode (str): The file mode to open the file with.
            encoding: The type of encoding to use.
            delay (bool): Add a delay to the logging.
            level (str or int, optional): The level which the logger will start logging.
        """
        if isinstance(level, str):
            level = self.get_level(level)
        handler = logging.FileHandler(filename, mode, encoding, delay)
        handler.setLevel(level)
        formatter = PreciseFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    # Override Logger Methods
    def log(self, level, msg, *args, append=None, **kwargs):
        """Creates a log entry based on provided level.

        Args:
            level (str or int): The level to create log entry for.
            msg (str): The message to add to the log.
            *args: The arguments for the original log method.
            append (bool, optional): Determines if append message should be added. Defaults to attribute if left None.
            **kwargs: The key word arguments for the original log method.
        """
        if isinstance(level, str):
            level = self.levels[level]

        if not self.quick_check or self.isEnabledFor(level):
            if append or (append is None and self.allow_append):
                msg = self.append_message + msg
            self._logger.log(level, msg, *args, **kwargs)

    def debug(self, msg, *args, append=None, **kwargs):
        """Creates a debug log.

        Args:
            msg (str): The message to add to the log.
            *args: The arguments for the original log method.
            append (bool, optional): Determines if append message should be added. Defaults to attribute if left None.
            **kwargs: The key word arguments for the original log method.
        """
        if not self.quick_check or self.isEnabledFor(self.levels["DEBUG"]):
            if append or (append is None and self.allow_append):
                msg = self.append_message + msg
            self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, append=None, **kwargs):
        """Creates an info log.

        Args:
            msg (str): The message to add to the log.
            *args: The arguments for the original log method.
            append (bool, optional): Determines if append message should be added. Defaults to attribute if left None.
            **kwargs: The key word arguments for the original log method.
        """
        if not self.quick_check or self.isEnabledFor(self.levels["INFO"]):
            if append or (append is None and self.allow_append):
                msg = self.append_message + msg
            self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, append=None, **kwargs):
        """Creates a warning log.

        Args:
            msg (str): The message to add to the log.
            *args: The arguments for the original log method.
            append (bool, optional): Determines if append message should be added. Defaults to attribute if left None.
            **kwargs: The key word arguments for the original log method.
        """
        if not self.quick_check or self.isEnabledFor(self.levels["WARNING"]):
            if append or (append is None and self.allow_append):
                msg = self.append_message + msg
            self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, append=None, **kwargs):
        """Creates an error log.

        Args:
            msg (str): The message to add to the log.
            *args: The arguments for the original log method.
            append (bool, optional): Determines if append message should be added. Defaults to attribute if left None.
            **kwargs: The key word arguments for the original log method.
        """
        if not self.quick_check or self.isEnabledFor(self.levels["ERROR"]):
            if append or (append is None and self.allow_append):
                msg = self.append_message + msg
            self._logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, append=None, **kwargs):
        """Creates a critical log.

        Args:
            msg (str): The message to add to the log.
            *args: The arguments for the original log method.
            append (bool, optional): Determines if append message should be added. Defaults to attribute if left None.
            **kwargs: The key word arguments for the original log method.
        """
        if not self.quick_check or self.isEnabledFor(self.levels["CRITICAL"]):
            if append or (append is None and self.allow_append):
                msg = self.append_message + msg
            self._logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, append=None, **kwargs):
        """Creates an exception log.

        Args:
            msg (str): The message to add to the log.
            *args: The arguments for the original log method.
            append (bool, optional): Determines if append message should be added. Defaults to attribute if left None.
            **kwargs: The key word arguments for the original log method.
        """
        if not self.quick_check or self.isEnabledFor(self.levels["EXCEPTION"]):
            if append or (append is None and self.allow_append):
                msg = self.append_message + msg
            self._logger.exception(msg, *args, **kwargs)

    # New Logger Methods
    def trace_log(self, class_, func, msg, *args, name="", level=None, append=None, **kwargs):
        """The creates a log with traceback formatting.

        Args:
            class_ (str): The name of class this log is being made from.
            func (str): The name of function/method this log is being made from.
            msg (str): The name of class this log is being made from.
            *args: The arguments for the original log method.
            name (str, optional): The an additional identifier that can be used to trace this log.
            level (str or int, optional): The level to create log entry for.
            append (bool, optional): Determines if append message should be added. Defaults to attribute if left None.
            **kwargs: The key word arguments for the original log method.
        """
        if level is None:
            level = self._logger.level
        elif isinstance(level, str):
            level = self.levels[level]

        if not self.quick_check or self.isEnabledFor(level):
            trace_msg = f"{class_}({name}) -> {func}: {msg}"
            self.log(level, trace_msg, *args, append=append, **kwargs)


class WarningsLogger(AdvancedLogger):
    """An AdvancedLogger which specifically captures the warnings from the 'warnings' module.

    This class interfaces with the 'warnings' module to handle warnings by replacing the 'showwarning' handling
    function. This is the only handling function this class is interfacing with so the methods are class methods because
    any modification to the 'showwarning' will be global and the instance's of this class all need to know the changes.
    Also, this class allows the 'showwarning' be easily reassigned so the exact handling warnings can be tailored to
    the application. The 'showwarning' function has boilerplate which does not change much between applications. To help
    with this, there is a 'showwarning' factory which creates 'showwarning' functions with the boilerplate embedded and
    only needs a 'warning_handler' function passed to it.

    Class Attributes:
        _warnings_showwarning: The original warnings.showwarning function that this class overrides to capture warnings.
        capturing (bool): A state which indicates if the class is capturing warnings.
        default_logger_name (str): The default name of the default logger to send the warnings.
        current_showwarning: The function that will replace warnings.showwarning while capturing warnings.
        warning_handler: The function that will handle how a warning is logged.

    Args:
        obj: The logger that this object will wrap or the name of the logger to create.
        module_of_class (str, optional): The name of module the class originates from.
        capture (bool, optional): Determines if warning capturing should start on initialization.
        default (bool, optional): Determines if the warning capturing should be set to the default functions.
        init (bool, optional): Determines if this object should be initialized.
    """
    _warnings_showwarning = None
    capturing = False
    default_logger_name = "py.warnings"
    current_showwarning = None
    warning_handler = None

    # Class Methods
    @classmethod
    def capture_warnings(cls, capture=True, init=False):
        """Determines if warnings will be redirected to the logging package.

        The redirect is a global effect and logs to specifically to the 'py.warnings' logger.

        Args:
            capture (bool, optional): Determines if warnings will be redirected to the logging package.
            init (bool, optional): Determines if the default logging warning handling will be used.
        """
        if capture:
            if cls._warnings_showwarning is None:
                cls._warnings_showwarning = warnings.showwarning
                if init:
                    cls.set_showwarning()
                cls.capturing = True
        else:
            if cls._warnings_showwarning is not None:
                warnings.showwarning = cls._warnings_showwarning
                cls.capturing = False

    # Create
    @classmethod
    def default_warning_handler(cls, name=None):
        """Creates the default warning handler function for handling warnings to log.

        Args:
            name (str, optional): The name of the logger which the warnings will be logged to.

        Returns:
            func: The warning handler function
        """
        if name is None:
            name = cls.default_logger_name

        def warning_handler(message, category, filename, lineno, line):
            """A function that handles a warning to be logged.

            Args:
                message: The warning message.
                category: The warning category.
                filename: The filename to output the warning to.
                lineno: The line number of the warning.
                line: The code of line of the warning.
            """
            s = warnings.formatwarning(message, category, filename, lineno, line)
            logger = logging.getLogger(name)
            if not logger.handlers:
                logger.addHandler(logging.NullHandler())
            logger.warning("%s", s)

        return warning_handler

    @classmethod
    def default_showwarning(cls, warning_handler=None):
        """Creates the default showwarning function to be used to capture the warnings from the warnings module

        Args:
            warning_handler: The function which will handle the captured warning.

        Returns:
            func: The showwarning function
        """
        # Check if original warnings.showwarning function is saved.
        if cls._warnings_showwarning is None:
            raise NotImplementedError("capture warnings must be enabled before creating showwarning")

        # Variables to create showwarning with
        if warning_handler is None:
            warning_handler = cls.warning_handler
        _warnings_showwarning = cls._warnings_showwarning

        # Create showwarning
        def showwarning(message, category, filename, lineno, file=None, line=None):
            """Normally, writes a warning to a file, but now sends to a warning handler.

            Args:
                message: The warning message.
                category: The warning category.
                filename: The filename to output the warning to.
                lineno: The line number of the warning.
                line: The code of line of the warning.
            """
            if file is not None:
                _warnings_showwarning(message, category, filename, lineno, file, line)
            else:
                warning_handler(message, category, filename, lineno, line)

        return showwarning

    # Setter/Getters
    @classmethod
    def set_warning_handler(cls, warning_handler=None):
        """Sets the warning handler to the given func or the default warning handler if there is none.

        Args:
            warning_handler: The function to set the warning handler to.
        """
        if warning_handler is None:
            warning_handler = cls.default_warning_handler()

        # Set cls.warning_handler to the new showwarning
        if cls.warning_handler is not None:
            del cls.warning_handler
        cls.warning_handler = warning_handler

    @classmethod
    def set_showwarning(cls, showwarning=None, warning_handler=None):
        """Sets the showwarning function to the given func or the default showwarning function if there is none.

        Args:
            showwarning: The function to set the showwarning function to.
            warning_handler: The function to set the warning handler to if a default showwarning function must be create
        """
        # Creates showwarning if showwarning is not given
        if showwarning is None:
            if warning_handler is None:
                cls.set_warning_handler(warning_handler)
            showwarning = cls.default_showwarning(warning_handler)

        # Set cls._current_showwarning to the new showwarning
        if cls.current_showwarning is not None:
            del cls.current_showwarning
        cls.current_showwarning = showwarning

        # Sets warnings.showwarning
        warnings.showwarning = showwarning

    # Construction/Destruction
    def __init__(self, obj=None, module_of_class="(Not Given)", capture=False, default=False, init=True):
        super().__init__(init=False)

        if init:
            self.construct(obj, module_of_class, capture, default)

    def construct(self, obj=None, module_of_class="(Not Given)", capture=False, default=False):
        """The constructor for this object.

        Args:
            obj: The logger that this object will wrap or the name of the logger to create.
            module_of_class (str, optional): The name of module the class originates from.
            capture (bool, optional): Determines if warning capturing should start on initialization.
            default (bool, optional): Determines if the warning capturing should be set to the default functions.
        """
        super().construct(obj, module_of_class)
        if capture:
            self.capture_warnings(init=default)

    # Methods
    def create_warning_handler(self):
        """Creates a warning handler function which uses this instance as the logger to handle the warning.

        Returns:
            func: The warning handler function
        """
        def warning_handler(message, category, filename, lineno, line):
            """A function that handles a warning to be logged.

            Args:
                message: The warning message.
                category: The warning category.
                filename: The filename to output the warning to.
                lineno: The line number of the warning.
                line: The code of line of the warning.
            """
            s = warnings.formatwarning(message, category, filename, lineno, line)
            self.warning("%s", s)

        return warning_handler

    def create_showwarning(self, warning_handler=None):
        """Creates a showwarning function to be used to capture the warnings from the warnings module.

        Args:
            warning_handler: The function which will handle the captured warning.

        Returns:
            func: The showwarning function
        """
        return self.default_showwarning(warning_handler)

    # Setters/Getters
    def set_warning_logger(self, warning_handler=None, showwarning=None):
        """Sets the warning capturing with this instance's methods if nothing is given.

        Args:
            warning_handler: The function to set the warning handler to if a default showwarning function must be create
            showwarning: The function to set the showwarning function to.
        """
        if showwarning is None:
            if warning_handler is None:
                warning_handler = self.create_warning_handler()
                self.set_warning_handler(warning_handler)
            self.create_showwarning(warning_handler)
        self.set_showwarning(showwarning)


# Todo: Add Performance Testing (logging?)
class PerformanceLogger(AdvancedLogger):
    default_timer = time.perf_counter

    # Methods
    # Construction/Destruction
    def __init__(self, obj=None, timer=None, module_of_class="(Not Given)", init=True):
        super().__init__(obj=obj, module_of_class=module_of_class, init=False)

        self.timer = self.default_timer
        self.marks = {}
        self.pairs = {}

        if init:
            self.construct(timer=timer, obj=obj)

    def construct(self, obj=None, timer=None):
        super().construct(obj=obj)
        if timer is not None:
            self.timer = timer

    # Time Tacking
    def time_func(self, func, kwargs={}):
        start = self.timer()
        func(**kwargs)
        stop = self.timer()
        return stop - start

    def mark(self, name):
        self.marks[name] = self.timer()

    def mark_difference(self, f_name, s_name):
        return self.marks[f_name] - self.marks[s_name]

    def pair_begin(self, type_, name=None):
        if type_ not in self.pairs:
            self.pairs[type_] = {}
        if name is None:
            name = len(self.pairs[type_])
        self.pairs[type_][name] = {"beginning": self.timer(), "ending": None}

    def pair_end(self, type_, name=None):
        if name is None:
            name = list(self.pairs[type_].keys())[0]
        self.pairs[type_][name]["ending"] = self.timer()

    def pair_difference(self, type_, name=None):
        if name is None:
            name = list(self.pairs[type_].keys())[0]
        pair = self.pairs[type_][name]
        return pair["ending"] - pair["beginning"]

    def pair_average_difference(self, type_):
        differences = []
        for pair in self.pairs[type_].values():
            differences.append(pair["ending"] - pair["beginning"])
        return statistics.mean(differences), statistics.stdev(differences)

    # Logging
    def log_pair_average_difference(self, type_, *args, append=None, level="DEBUG", **kwargs):
        if isinstance(level, str):
            level = self.get_level(level)
        mean, std = self.pair_average_difference(type_)
        msg = f"{type_} had a difference of {mean} ± {std}."
        self.log(level, msg, *args, append=append, **kwargs)

