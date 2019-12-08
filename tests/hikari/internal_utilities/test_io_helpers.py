#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Nekoka.tt 2019-2020
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
import io

import pytest

from hikari.internal_utilities import io_helpers


@pytest.mark.parametrize(
    ["input", "expected_result_type"],
    [
        ("hello", io.StringIO),
        (b"hello", io.BytesIO),
        (bytearray("hello", "utf-8"), io.BytesIO),
        (memoryview(b"hello"), io.BytesIO),
    ],
)
def test_make_resource_seekable(input, expected_result_type):
    assert isinstance(io_helpers.make_resource_seekable(input), expected_result_type)
