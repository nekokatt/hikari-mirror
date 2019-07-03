#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Nekoka.tt 2019
#
# This file is part of Hikari.
#
# Hikari is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hikari is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Hikari. If not, see <https://www.gnu.org/licenses/>.

"""
Type checking compatibility.

This namespace contains the entirety of the :mod:`typing` module. Any members documented below are assumed to
*override* the original implementation if it exists for your target platform implementation and Python version.
"""
import typing as _typing

# noinspection PyUnresolvedReferences
from typing import *

#: Not implemented by PyPy3.6
NoReturn = getattr(_typing, "NoReturn", None)

try:
    raise RuntimeError
except RuntimeError as __ex:
    #: Type of a traceback.
    TracebackType = type(__ex.__traceback__)
    del __ex
