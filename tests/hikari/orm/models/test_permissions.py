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

import pytest

from hikari.orm.models import permissions


@pytest.mark.model
def test_Permission_all():
    all = permissions.Permission.all()

    sum_permissions = 0
    for pm in permissions.Permission.__members__.values():
        sum_permissions |= pm

    assert bin(sum_permissions) == bin(all)


@pytest.mark.model
def test_permission_module___getattr__():
    assert permissions.MANAGE_MESSAGES == permissions.Permission.MANAGE_MESSAGES
