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
import datetime
from unittest import mock

import pytest

from hikari.orm import fabric
from hikari.orm import state_registry
from hikari.orm.models import guilds
from hikari.orm.models import members
from hikari.orm.models import presences
from hikari.orm.models import roles
from hikari.orm.models import users
from tests.hikari import _helpers


@pytest.fixture()
def mock_state_registry():
    return mock.MagicMock(spec_set=state_registry.BaseStateRegistry)


@pytest.fixture()
def fabric_obj(mock_state_registry):
    return fabric.Fabric(state_registry=mock_state_registry)


@pytest.mark.model
def test_Member_with_filled_fields(fabric_obj):
    user_dict = {
        "id": "123456",
        "username": "Boris Johnson",
        "discriminator": "6969",
        "avatar": "1a2b3c4d",
        "locale": "gb",
        "flags": 0b00101101,
        "premium_type": 0b1101101,
    }
    guild_obj = _helpers.mock_model(guilds.Guild, id=12345)
    member_obj = members.Member(
        fabric_obj,
        guild_obj,
        {
            "nick": "foobarbaz",
            "roles": ["11111", "22222", "33333", "44444"],
            "joined_at": "2015-04-26T06:26:56.936000+00:00",
            "premium_since": "2019-05-17T06:26:56.936000+00:00",
            # These should be completely ignored.
            "deaf": False,
            "mute": True,
            "user": user_dict,
        },
    )

    assert member_obj.nick == "foobarbaz"
    assert member_obj.joined_at == datetime.datetime(2015, 4, 26, 6, 26, 56, 936000, datetime.timezone.utc)
    assert member_obj.premium_since == datetime.datetime(2019, 5, 17, 6, 26, 56, 936000, datetime.timezone.utc)
    assert member_obj.is_deaf is False
    assert member_obj.is_mute is True
    assert member_obj.guild is guild_obj
    assert member_obj.presence is None
    fabric_obj.state_registry.parse_user.assert_called_with(user_dict)


@pytest.mark.model
def test_Member_with_no_optional_fields(fabric_obj):
    user_dict = {"id": "123456", "username": "Boris Johnson", "discriminator": "6969", "avatar": "1a2b3c4d"}
    guild_obj = _helpers.mock_model(guilds.Guild, id=12345)
    member_obj = members.Member(
        fabric_obj,
        guild_obj,
        {
            "roles": ["11111", "22222", "33333", "44444"],
            "joined_at": "2015-04-26T06:26:56.936000+00:00",
            "user": user_dict,
        },
    )

    assert member_obj.nick is None
    assert member_obj.joined_at == datetime.datetime(2015, 4, 26, 6, 26, 56, 936000, datetime.timezone.utc)
    assert member_obj.premium_since is None
    assert member_obj.is_deaf is False
    assert member_obj.is_mute is False
    assert member_obj.guild is guild_obj
    assert member_obj.presence is None
    fabric_obj.state_registry.parse_user.assert_called_with(user_dict)


@pytest.mark.model
def test_Member_update_state(fabric_obj):
    role_one = _helpers.mock_model(roles.Role)
    role_two = _helpers.mock_model(roles.Role)
    role_three = _helpers.mock_model(roles.Role)

    role_objs = [role_one, role_two, role_three]

    user_dict = {"id": "123456", "username": "Boris Johnson", "discriminator": "6969", "avatar": "1a2b3c4d"}
    guild_obj = _helpers.mock_model(guilds.Guild, id=12345)
    member_obj = members.Member(
        fabric_obj,
        guild_obj,
        {
            "roles": ["11111", "22222", "33333", "44444"],
            "joined_at": "2015-04-26T06:26:56.936000+00:00",
            "premium_since": "2019-05-17T06:26:56.936000+00:00",
            "user": user_dict,
        },
    )

    member_obj.update_state(role_objs, {"nick": "potato", "deaf": True, "mute": True})
    assert member_obj.nick == "potato"
    assert member_obj.is_deaf is True
    assert member_obj.is_mute is True
    assert member_obj.premium_since is None
    assert member_obj.roles == role_objs


@pytest.mark.model
def test_Member_user_accessor(fabric_obj):
    user_obj = mock.MagicMock(spec_set=users.User)
    guild_obj = mock.MagicMock(spec_set=guilds.Guild)
    # Member's state is delegated to the inner user.
    user_obj._fabric = fabric_obj
    fabric_obj.state_registry.parse_user = mock.MagicMock(return_value=user_obj)
    fabric_obj.state_registry.get_guild_by_id = mock.MagicMock(return_value=guild_obj)
    member_obj = members.Member(
        fabric_obj, guild_obj, {"joined_at": "2019-05-17T06:26:56.936000+00:00", "user": user_obj}
    )
    assert member_obj.user is user_obj


@pytest.mark.model
def test_Member_guild_accessor(fabric_obj):
    user_obj = mock.MagicMock(spec_set=users.User)
    guild_obj = mock.MagicMock(spec_set=guilds.Guild)
    # Member's state is delegated to the inner user.
    user_obj._fabric = fabric
    fabric_obj.state_registry.parse_user = mock.MagicMock(return_value=user_obj)
    m = members.Member(
        fabric_obj, guild_obj, {"joined_at": "2019-05-17T06:26:56.936000+00:00", "user": user_obj, "guild_id": 1234}
    )
    assert m.guild is guild_obj


def test_Member_update_presence_state(fabric_obj):
    guild_obj = mock.MagicMock(guilds.Guild)
    mock_presence = mock.MagicMock(presences.Presence)
    fabric_obj.state_registry.parse_user.return_value = mock.MagicMock(users.User, _fabric=fabric_obj, id=123456)
    fabric_obj.state_registry.parse_presence.return_value = mock_presence
    presence_payload = {
        "user": {"id": "123456"},
        "status": "online",
        "game": None,
        "client_status": {"desktop": "online"},
        "activities": [],
        "roles": [],
        "guild_id": "2331123",
    }
    member_obj = members.Member(
        fabric_obj,
        guild_obj,
        {
            "roles": [],
            "joined_at": "2015-04-26T06:26:56.936000+00:00",
            "premium_since": "2019-05-17T06:26:56.936000+00:00",
            "user": {},
        },
    )
    assert member_obj.presence is None
    member_obj.update_presence_state(presence_payload)
    fabric_obj.state_registry.parse_presence.assert_called_once_with(member_obj, presence_payload)
    assert member_obj.presence is mock_presence


@_helpers.assert_raises(type_=ValueError)
def test_Member_update_presence_state_with_mismatching_presence(fabric_obj):
    guild_obj = mock.MagicMock(guilds.Guild)
    presence_payload = {
        "user": {"id": "123456"},
        "status": "online",
        "game": None,
        "client_status": {"desktop": "online"},
        "activities": [],
        "roles": [],
        "guild_id": "5321321",
    }
    fabric_obj.state_registry.parse_user.return_value = mock.MagicMock(users.User, id=4123)
    member_obj = members.Member(
        fabric_obj,
        guild_obj,
        {
            "roles": [],
            "joined_at": "2015-04-26T06:26:56.936000+00:00",
            "premium_since": "2019-05-17T06:26:56.936000+00:00",
            "user": {},
        },
    )
    member_obj.update_presence_state(presence_payload)


@pytest.mark.model
def test_Member___repr__():
    assert repr(
        _helpers.mock_model(
            members.Member,
            id=69,
            username="bar",
            discriminator=1234,
            is_bot=True,
            guild=_helpers.mock_model(guilds.Guild, id=42, name="foo"),
            nick="baz",
            joined_at=datetime.datetime.fromtimestamp(101).replace(tzinfo=datetime.timezone.utc),
            __repr__=members.Member.__repr__,
        )
    )
