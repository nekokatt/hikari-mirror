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
Reactions to a message.
"""
__all__ = "Reaction"

import typing

from hikari.core.model import base
from hikari.core.model import emoji
from hikari.core.model import model_cache
from hikari.core.utils import transform


@base.dataclass()
class Reaction:
    """
    Model for a message reaction object
    """

    __slots__ = ("_state", "count", "me", "emoji")

    _state: typing.Any
    # The number of times the emoji has been used to react
    count: int
    # Whether the current user has reacted with the emoji or not
    me: bool
    # The emoji used for the reaction
    emoji: "emoji.Emoji"

    @staticmethod
    def from_dict(global_state: model_cache.AbstractModelCache, payload):
        return Reaction(
            _state=global_state,
            count=transform.get_cast(payload, "count", int),
            me=transform.get_cast(payload, "me", bool),
            emoji=global_state.parse_emoji(payload.get("emoji")),
        )
