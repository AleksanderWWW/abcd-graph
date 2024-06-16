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


from functools import wraps
from typing import (
    TYPE_CHECKING,
    Callable,
)

from typing_extensions import (
    ParamSpec,
    TypeVar,
)

if TYPE_CHECKING:
    from abcd_graph.abcd import Graph

P = ParamSpec("P")
R = TypeVar("R")


def require(package_name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def deco(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except ImportError as e:
                raise ImportError(
                    f"Package '{package_name}' is required to use '{func.__name__}'. Run "
                    f"`pip install abcd_graph[{package_name}]` to install it."
                ) from e

        return wrapper

    return deco


def require_graph_built(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(self: "Graph", *args: P.args, **kwargs: P.kwargs) -> R:
        if not self.is_built:
            raise RuntimeError("Graph has not been built yet")

        return func(self, *args, **kwargs)  # type: ignore[arg-type]

    return wrapper  # type: ignore[return-value]
