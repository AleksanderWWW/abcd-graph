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


__all__ = ["ABCDParams"]

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)


class ABCDParams(BaseModel):
    gamma: float = Field(description="Power-law parameter for degrees, between 2 and 3", kw_only=True, default=2.5)
    delta: int = Field(description="Min degree", kw_only=True, default=5)
    zeta: float = Field(description="Parameter for max degree, between 0 and 1", kw_only=True, default=0.5)
    beta: float = Field(
        description="Power-law parameter for community sizes, between 1 and 2",
        kw_only=True,
        default=1.5,
    )
    s: int = Field(description="Min community size", kw_only=True, default=20)
    tau: float = Field(description="Parameter for max community size, between zeta and 1", kw_only=True, default=0.8)
    xi: float = Field(description="Noise parameter, between 0 and 1", kw_only=True, default=0.25)

    @field_validator("gamma")
    @classmethod
    def check_gamma(cls, v: float) -> float:
        if v < 2 or v > 3:
            raise ValueError("gamma must be between 2 and 3")
        return v

    @field_validator("zeta")
    @classmethod
    def check_zeta(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("zeta must be between 0 and 1")
        return v

    @field_validator("beta")
    @classmethod
    def check_beta(cls, v: float) -> float:
        if v < 1 or v > 2:
            raise ValueError("beta must be between 1 and 2")
        return v

    @field_validator("tau")
    @classmethod
    def check_tau(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("tau must be between 0 and 1")
        return v

    @field_validator("xi")
    @classmethod
    def check_xi(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("xi must be between 0 and 1")
        return v
