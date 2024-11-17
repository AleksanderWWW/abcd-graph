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

__all__ = [
    "construct_logger",
]

import logging
import os
from abc import (
    ABC,
    abstractmethod,
)
from typing import Union

from typing_extensions import TypeAlias


class ABCDLogger(ABC):  # pragma: no cover
    @abstractmethod
    def info(self, message: str) -> None:
        pass

    @abstractmethod
    def debug(self, message: str) -> None:
        pass

    @abstractmethod
    def warning(self, message: str) -> None:
        pass

    @abstractmethod
    def error(self, message: str) -> None:
        pass

    @abstractmethod
    def critical(self, message: str) -> None:
        pass


class NoOpLogger(ABCDLogger):
    def info(self, message: str) -> None:
        pass

    def debug(self, message: str) -> None:
        pass

    def warning(self, message: str) -> None:
        pass

    def error(self, message: str) -> None:
        pass

    def critical(self, message: str) -> None:
        pass


class StdOutLogger(ABCDLogger):
    NAME = "abcd-graph"

    def __init__(self) -> None:
        logging_level = int(os.getenv("ABCD_LOG", logging.INFO))
        logging.basicConfig(
            level=logging_level,
            format="[%(name)s] - %(asctime)s - %(levelname)s - %(message)s",
        )
        self.logging_level = logging_level
        self.logger = logging.getLogger(self.NAME)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def critical(self, message: str) -> None:
        self.logger.critical(message)


LoggerType: TypeAlias = Union[ABCDLogger, bool]


def construct_logger(logger: bool) -> ABCDLogger:
    return StdOutLogger() if logger else NoOpLogger()
