# Copyright (c) 2024 Jordan Barrett & Aleksander Wojnarowicz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import logging
import os
from unittest.mock import patch

from abcd_graph.logger import (
    NoOpLogger,
    StdOutLogger,
    construct_logger,
)


def test_construct_logger():
    assert isinstance(construct_logger(False), NoOpLogger)
    assert isinstance(construct_logger(True), StdOutLogger)


def test_default_logging_level(caplog):
    logger = StdOutLogger()
    caplog.set_level(logger.logging_level)

    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")

    captured_stdout = caplog.text

    assert "debug" not in captured_stdout
    assert "info" in captured_stdout
    assert "warning" in captured_stdout
    assert "error" in captured_stdout
    assert "critical" in captured_stdout


@patch.dict(os.environ, {"ABCD_LOG": f"{logging.CRITICAL}"})
def test_env_var_for_logging_level(caplog):
    logger = StdOutLogger()
    caplog.set_level(logger.logging_level)

    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")

    captured_stdout = caplog.text

    assert "debug" not in captured_stdout
    assert "info" not in captured_stdout
    assert "warning" not in captured_stdout
    assert "error" not in captured_stdout
    assert "critical" in captured_stdout


def test_noop_logger(caplog):
    logger = NoOpLogger()

    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")

    captured_stdout = caplog.text

    assert "debug" not in captured_stdout
    assert "info" not in captured_stdout
    assert "warning" not in captured_stdout
    assert "error" not in captured_stdout
    assert "critical" not in captured_stdout
