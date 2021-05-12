#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" test_advancedlogging.py
Test for the advancedlogging package
"""
__author__ = "Anthony Fong"
__copyright__ = "Copyright 2021, Anthony Fong"
__credits__ = ["Anthony Fong"]
__license__ = ""
__version__ = "0.1.0"
__maintainer__ = "Anthony Fong"
__email__ = ""
__status__ = "Beta"

# Default Libraries #
import pathlib
import warnings

# Downloaded Libraries #
import pytest

# Local Libraries #
import src.advancedlogging as advancedlogging


# Definitions #
# Functions #
@pytest.fixture
def tmp_dir(tmpdir):
    """A pytest fixture that turn the tmpdir into a Path object."""
    return pathlib.Path(tmpdir)


# Classes #
class ClassTest:
    """Default class tests that all classes should pass."""
    class_ = None

    def test_instant_creation(self):
        assert isinstance(self.class_(), self.class_)


class BaseAdvancedLoggerTest(ClassTest):
    """All AdvancedLogger subclasses need to pass these tests to be considered functional."""
    class_ = None
    logger_name = "base"

    def get_log_lines(self, tmp_dir):
        path = tmp_dir.joinpath(f"{self.logger_name}.log")
        with path.open() as f_object:
            lines = f_object.readlines()
        return lines

    @pytest.fixture
    def logger(self):
        return self.class_(self.logger_name)

    @pytest.fixture
    def get_default_file_handler(self, logger, tmp_dir):
        path = tmp_dir.joinpath(f"{self.logger_name}.log")
        logger.add_default_file_handler(filename=path)
        return logger

    def test_instantiation(self, logger):
        assert logger.name == self.logger_name

    def test_default_file_handler(self, get_default_file_handler, logger):
        assert len(logger.handlers) > 0

    def test_default_file_write(self, get_default_file_handler, logger, tmp_dir):
        log_str = "Test log entry read."
        logger.setLevel("INFO")
        logger.info(log_str)
        lines = self.get_log_lines(tmp_dir)
        count = len(lines)
        assert count == 1
        assert log_str in lines[0]


class TestAdvancedLogger(BaseAdvancedLoggerTest):
    """Tests the AdvancedLogger"""
    class_ = advancedlogging.AdvancedLogger
    logger_name = "full"

    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_trace_log(self, get_default_file_handler, logger, tmp_dir, level):
        log_class_ = self.class_
        log_func = "test_trace_log"
        log_str = "Test traceback"
        logger.setLevel(level)

        logger.trace_log(log_class_, log_func, log_str)

        lines = self.get_log_lines(tmp_dir)
        count = len(lines)
        assert count == 1
        assert log_func in lines[0]
        assert level in lines[0]
        assert log_str in lines[0]


class TestWarningLogger(BaseAdvancedLoggerTest):
    """Tests the WarningLogger"""
    class_ = advancedlogging.WarningsLogger
    logger_name = "warnings"

    @pytest.mark.skip
    def test_set_warning_logger(self, get_default_file_handler, logger, tmp_dir):
        # Setup Logger
        logger.capture_warnings(True)
        logger.set_warning_logger()

        # Throw Warning
        warnings.warn("Test")

        # Check Log
        path = tmp_dir.joinpath(f"{self.logger_name}.log")
        with path.open() as f_object:
            lines = f_object.readlines()
            count = len(lines)
            assert count == 1
            print(lines)


class TestPerformanceLogger(BaseAdvancedLoggerTest):
    """Tests the PerformanceLogger"""
    class_ = advancedlogging.PerformanceLogger
    logger_name = "performance"

