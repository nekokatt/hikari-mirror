#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Nekokatt 2019-2020
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
Members that represent users and their state in specific guilds.
"""
from __future__ import annotations

__all__ = ["Member", "MemberLikeT"]

import datetime
import typing

from hikari.internal_utilities import assertions
from hikari.internal_utilities import containers
from hikari.internal_utilities import dates
from hikari.internal_utilities import delegate
from hikari.internal_utilities import reprs
from hikari.internal_utilities import transformations
from hikari.orm.models import bases
from hikari.orm.models import guilds
from hikari.orm.models import presences
from hikari.orm.models import users


@delegate.delegate_to(users.User, "user")
class Member(users.User, delegate_fabricated=True):
    """
    A specialization of a user which provides implementation details for a specific guild.

    This is a delegate type, meaning it subclasses a :class:`User` and implements it by deferring inherited calls
    and fields to a wrapped user object which is shared with the corresponding member in every guild the user is in.
    """

    __slots__ = ("user", "guild", "role_ids", "joined_at", "nick", "premium_since", "presence", "is_deaf", "is_mute")

    #: The underlying user object.
    user: users.User

    #: The guild that the member is in.
    guild: guilds.Guild

    #: The IDs of the roles the member has.
    role_ids: typing.Sequence[int]

    #: The date and time the member joined this guild.
    #:
    #: :type: :class:`datetime.datetime`
    joined_at: datetime.datetime

    #: The optional nickname of the member.
    #:
    #: :type: :class:`str` or `None`
    nick: typing.Optional[str]

    #: The optional date/time that the member Nitro-boosted the guild.
    #:
    #: :type: :class:`datetime.datetime` or `None`
    premium_since: typing.Optional[datetime.datetime]

    #: Whether the user is deafened in voice.
    #:
    #: :type: :class:`bool`
    is_deaf: bool

    #: Whether the user is muted in voice.
    #:
    #: :type: :class:`bool`
    is_mute: bool

    #: The user's online presence. This will be `None` until populated by a gateway event.
    #:
    #: :type: :class:`hikari.orm.models.presences.Presence` or `None`
    presence: typing.Optional[presences.MemberPresence]

    __copy_by_ref__ = ("presence", "guild")

    __repr__ = reprs.repr_of("id", "username", "discriminator", "is_bot", "guild.id", "guild.name", "nick", "joined_at")

    # noinspection PyMissingConstructor
    def __init__(self, fabric_obj: typing.Any, guild: guilds.Guild, payload: typing.Dict) -> None:
        self.presence = None
        self.user = fabric_obj.state_registry.parse_user(payload["user"])
        self.guild = guild
        self.joined_at = dates.parse_iso_8601_ts(payload["joined_at"])
        self.update_state(payload)

    def update_state(self, payload: typing.Dict) -> None:
        if "roles" in payload:
            self.role_ids = [int(role_id) for role_id in payload.get("roles", containers.EMPTY_SEQUENCE)]

        if "premium_since" in payload:
            self.premium_since = transformations.nullable_cast(payload.get("premium_since"), dates.parse_iso_8601_ts)

        if "nick" in payload:
            self.nick = payload.get("nick")

        if "deaf" in payload:
            self.is_deaf = payload.get("deaf", False)

        if "mute" in payload:
            self.is_mute = payload.get("mute", False)


#: A :class:`Member`, or an :class:`int`/:class:`str` ID of one.
MemberLikeT = typing.Union[bases.RawSnowflakeT, Member]
