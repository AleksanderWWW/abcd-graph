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

import datetime
from abc import ABC
from dataclasses import dataclass
from typing import Optional

from abcd_graph.exporter import GraphExporter
from abcd_graph.graph.core.abcd_objects import GraphImpl
from abcd_graph.models import Model
from abcd_graph.params import ABCDParams


@dataclass
class BuildContext:
    model_used: Model
    start_time: datetime.datetime
    params: ABCDParams
    number_of_nodes: int
    end_time: Optional[datetime.datetime] = None
    raw_build_time: Optional[float] = None


class ABCDCallback(ABC):
    def before_build(self, context: BuildContext) -> None: ...

    def after_build(self, graph: GraphImpl, context: BuildContext, exporter: GraphExporter) -> None: ...
