#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" test_advancedlogging.py
Test for the advancedlogging package
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
import logging.handlers
import pathlib
import pickle
import queue
import timeit
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
    timeit_runs = 1000
    speed_tolerance = 200

    # def test_instant_creation(self):
    #     assert isinstance(self.class_(), self.class_)


class BaseAdvancedLoggerTest(ClassTest):
    """All AdvancedLogger subclasses need to pass these tests to be considered functional."""
    class_ = None
    logger_name = "base"

    def get_log_lines(self, tmp_dir):
        path = tmp_dir.joinpath(f"{self.logger_name}.log")
        with path.open() as f_object:
            lines = f_object.readlines()
        return lines

    def normal_logger(self):
        return self.class_(self.logger_name)

    def pickle_logger(self):
        obj = self.normal_logger()
        pickle_jar = pickle.dumps(obj)
        return pickle.loads(pickle_jar)

    @pytest.fixture(params=[normal_logger, pickle_logger])
    def logger(self, request):
        return request.param(self)

    @pytest.fixture
    def get_default_file_handler(self, logger, tmp_dir):
        path = tmp_dir.joinpath(f"{self.logger_name}.log")
        logger.add_default_file_handler(filename=path)
        return logger

    def test_instantiation(self):
        assert self.normal_logger().name == self.logger_name

    def test_pickle(self):
        obj = self.normal_logger()
        pickle_jar = pickle.dumps(obj)
        new_obj = pickle.loads(pickle_jar)
        assert set(dir(new_obj)) == set(dir(obj))

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

        logger.trace_log(log_class_, log_func, log_str, level=level)

        lines = self.get_log_lines(tmp_dir)
        count = len(lines)
        assert count == 1
        assert log_func in lines[0]
        assert level in lines[0]
        assert log_str in lines[0]

    @pytest.mark.xfail
    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_log_speed(self, logger, level):
        log_class_ = self.class_
        log_func = "test_trace_log"
        log_str = "Test traceback"
        logger.setLevel(level)

        def log():
            logger.trace_log(log_class_, log_func, log_str, level=level)

        def assignment():
            x = 10

        mean_new = timeit.timeit(log, number=self.timeit_runs) / self.timeit_runs * 1000000
        mean_old = timeit.timeit(assignment, number=self.timeit_runs) / self.timeit_runs * 1000000
        percent = (mean_new / mean_old) * 100

        print(f"\nNew speed {mean_new:.3f} μs took {percent:.3f}% of the time of the old function.")
        assert percent < self.speed_tolerance

    @pytest.mark.xfail
    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_log_skip_speed(self, logger, level):
        log_class_ = self.class_
        log_func = "test_trace_log"
        log_str = "Test traceback"
        logger.quick_check = False
        logger.setLevel("CRITICAL")

        def log():
            logger.trace_log(log_class_, log_func, log_str, level=level)

        def assignment():
            x = 10

        mean_new = timeit.timeit(log, number=self.timeit_runs) / self.timeit_runs * 1000000
        mean_old = timeit.timeit(assignment, number=self.timeit_runs) / self.timeit_runs * 1000000
        percent = (mean_new / mean_old) * 100

        print(f"\nNew speed {mean_new:.3f} μs took {percent:.3f}% of the time of the old function.")
        assert percent < self.speed_tolerance

    @pytest.mark.xfail
    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_log_skip_fast_speed(self, logger, level):
        log_class_ = self.class_
        logger.setLevel("CRITICAL")
        fast_logger = logger.deepcopy()
        fast_logger.quick_check = True
        logger.quick_check = False

        log_func = "test_trace_log"
        log_str = "Test traceback"

        def log():
            fast_logger.trace_log(log_class_, log_func, log_str, level=level)

        def original():
            logger.trace_log(log_class_, log_func, log_str, level=level)

        mean_new = timeit.timeit(log, number=self.timeit_runs) / self.timeit_runs * 1000000
        mean_old = timeit.timeit(original, number=self.timeit_runs) / self.timeit_runs * 1000000
        percent = (mean_new / mean_old) * 100

        print(f"\nNew speed {mean_new:.3f} μs took {percent:.3f}% of the time of the old function.")
        assert percent < self.speed_tolerance

    @pytest.mark.xfail
    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_log_queue_speed(self, get_default_file_handler, logger, level):
        log_class_ = self.class_
        logger.setLevel(level)

        que = queue.Queue(-1)
        queue_handler = logging.handlers.QueueHandler(que)
        logger.addHandler(queue_handler)

        log_func = "test_trace_log"
        log_str = "Test traceback"

        def log():
            logger.trace_log(log_class_, log_func, log_str, level=level)

        def assignment():
            x = 10

        mean_new = timeit.timeit(log, number=self.timeit_runs) / self.timeit_runs * 1000000
        mean_old = timeit.timeit(assignment, number=self.timeit_runs) / self.timeit_runs * 1000000
        percent = (mean_new / mean_old) * 100

        que.empty()

        print(f"\nNew speed {mean_new:.3f} μs took {percent:.3f}% of the time of the old function.")
        assert percent < self.speed_tolerance


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


# Main #
if __name__ == '__main__':
    pytest.main(["-v", "-s"])
