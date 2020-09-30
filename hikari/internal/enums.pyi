# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2020 Nekokatt
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
"""Typehints for `hikari.utilities.enums`."""

# Enums use a lot of internal voodoo that will not type check nicely, so we
# skip that module with MyPy and just accept that "here be dragons".
#
# The caveat to implementing this is that MyPy has to have a special module to
# understand how to use Python's enum types. I really don't want to have to
# ship my own MyPy plugin for this, so just make MyPy think that the types
# we are using are just aliases from the enum types in the standard library.

import enum as __enum
from typing import TypeVar as __TypeVar

Enum = __enum.Enum

__FlagT = __TypeVar("__FlagT", bound=__enum.IntFlag)

class IntFlag(__enum.IntFlag):
    def split(self: __FlagT) -> typing.Sequence[__FlagT]:
        ...
    def has_any(self: __FlagT, *flags: __FlagT) -> bool:
        ...
    def has_all(self: __FlagT, *flags: __FlagT) -> bool:
        ...
    def has_none(self, *flags: __FlagT) -> bool:
        ...

__all__ = ["Enum", "IntFlag"]
