#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" __init__.py

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

# Downloaded Libraries #

# Local Libraries #
from .advancedloggers import AdvancedLogger, WarningsLogger, PerformanceLogger
from .formatters import PreciseFormatter
from .objectswithlogging import ObjectWithLogging

# Main #
if __name__ == "__main__":
    # WarningLogger Example
    warning_logger = WarningsLogger("example_warning", capture=True)
    warning_logger.set_warning_logger()
    warning_logger.add_default_file_handler("example_warning.log")

    warnings.warn("This is a Test")

    # ObjectWithLogging Example
    # Define Classes
    class Example(ObjectWithLogging):
        class_loggers = {"example_root": AdvancedLogger("example_root")}

        # Class Methods
        @classmethod
        def build_class_loggers(cls):
            """Setup class loggers here"""
            cls.class_loggers["example_root"].setLevel("DEBUG")
            cls.class_loggers["example_root"].add_default_stream_handler()
            everyone_logger = AdvancedLogger("everyone")
            everyone_logger.add_default_file_handler("example_everyone.log")
            everyone_logger.setLevel("DEBUG")
            cls.class_loggers["everyone"] = everyone_logger

        # Construction/Destruction
        def __init__(self, name, a, b, init=True):
            super().__init__()
            self.name = ""
            self.a = 0
            self.b = 0

            if init:
                self.construct(name, a, b)

        # Methods
        # Construction/Destruction
        def construct(self, name, a, b):
            self.name = name
            self.a = a
            self.b = b

            self.build_loggers()

        # Loggers
        def build_loggers(self):
            """Setup object loggers here"""
            my_logger = self.class_loggers["everyone"].getChild(self.name)
            my_logger.add_default_file_handler(f"example_{self.name}.log")
            my_logger.add_default_stream_handler()
            my_logger.setLevel("DEBUG")
            my_logger.propagate = True
            self.loggers["my_logger"] = my_logger

        # Other Methods
        def add(self, x):
            self.a = self.a + x
            self.trace_log("my_logger", "add", f"some adding was done {self.a}", name=self.name)

        def subtract(self, x):
            self.a = self.a - x
            self.loggers["my_logger"].info("subtraction was done, but no traceback is hard")

        def divide(self, x):
            if x == 0:
                self.trace_log("my_logger", "divide", f"ZERO DIVISION WAS ATTEMPTED", name=self.name, level="CRITICAL")
            else:
                self. a = self.a / x
                self.loggers["example_root"].info("some division was done in an object somewhere")


    # Main Code
    Example.build_class_loggers()

    thing1 = Example("thing1", 1, 2)
    thing2 = Example("thing2", 3, 4)

    thing1.add(10)
    thing1.subtract(2)
    thing1.divide(0)

    thing2.add(230)
    thing2.divide(1)
