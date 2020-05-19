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
import contextlib
import datetime

import mock
import pytest

from hikari import application
from hikari.internal import conversions
from hikari.models import applications
from hikari.models import bases
from hikari.models import channels
from hikari.models import embeds
from hikari.models import emojis
from hikari.models import files
from hikari.models import guilds
from hikari.models import messages
from hikari.models import users
from tests.hikari import _helpers


@pytest.fixture
def test_attachment_payload():
    return {
        "id": "690922406474154014",
        "filename": "IMG.jpg",
        "size": 660521,
        "url": "https://somewhere.com/attachments/123/456/IMG.jpg",
        "_proxy_url": "https://media.somewhere.com/attachments/123/456/IMG.jpg",
        "width": 1844,
        "height": 2638,
    }


@pytest.fixture()
def test_emoji_payload():
    return {"id": "691225175349395456", "name": "test"}


@pytest.fixture
def test_reaction_payload(test_emoji_payload):
    return {"emoji": test_emoji_payload, "count": 100, "me": True}


@pytest.fixture
def test_message_activity_payload():
    return {"type": 5, "party_id": "ae488379-351d-4a4f-ad32-2b9b01c91657"}


@pytest.fixture
def test_message_crosspost_payload():
    return {"channel": "278325129692446722", "guild_id": "278325129692446720", "message_id": "306588351130107906"}


@pytest.fixture()
def test_application_payload():
    return {
        "id": "456",
        "name": "hikari",
        "description": "The best application",
        "icon": "2658b3029e775a931ffb49380073fa63",
        "cover_image": "58982a23790c4f22787b05d3be38a026",
    }


@pytest.fixture()
def test_user_payload():
    return {
        "bot": True,
        "id": "1234",
        "username": "cool username",
        "avatar": "6608709a3274e1812beb4e8de6631111",
        "discriminator": "0000",
    }


@pytest.fixture()
def test_member_payload(test_user_payload):
    return {"user": test_user_payload}


@pytest.fixture
def test_message_payload(
    test_application_payload,
    test_attachment_payload,
    test_reaction_payload,
    test_user_payload,
    test_member_payload,
    test_message_activity_payload,
    test_message_crosspost_payload,
):
    return {
        "id": "123",
        "channel": "456",
        "guild_id": "678",
        "author": test_user_payload,
        "member": test_member_payload,
        "content": "some info",
        "timestamp": "2020-03-21T21:20:16.510000+00:00",
        "edited_timestamp": "2020-04-21T21:20:16.510000+00:00",
        "tts": True,
        "mention_everyone": True,
        "mentions": [
            {"id": "5678", "username": "uncool username", "avatar": "129387dskjafhasf", "discriminator": "4532"}
        ],
        "mention_roles": ["987"],
        "mention_channels": [{"id": "456", "guild_id": "678", "type": 1, "name": "hikari-testing"}],
        "attachments": [test_attachment_payload],
        "embeds": [{}],
        "reactions": [test_reaction_payload],
        "pinned": True,
        "webhook_id": "1234",
        "type": 0,
        "activity": test_message_activity_payload,
        "application": test_application_payload,
        "message_reference": test_message_crosspost_payload,
        "flags": 2,
        "nonce": "171000788183678976",
    }


@pytest.fixture()
def mock_app():
    return mock.MagicMock(application.Application)


class TestAttachment:
    def test_deserialize(self, test_attachment_payload, mock_app):
        attachment_obj = messages.Attachment.deserialize(test_attachment_payload, app=mock_app)

        assert attachment_obj.id == 690922406474154014
        assert attachment_obj.filename == "IMG.jpg"
        assert attachment_obj.size == 660521
        assert attachment_obj.url == "https://somewhere.com/attachments/123/456/IMG.jpg"
        assert attachment_obj._proxy_url == "https://media.somewhere.com/attachments/123/456/IMG.jpg"
        assert attachment_obj.height == 2638
        assert attachment_obj.width == 1844

    @pytest.mark.asyncio
    async def test_aiter_yields_from_WebResourceStream(self):
        attachment = messages.Attachment(
            id=bases.Snowflake("1234"),
            filename="foobar.png",
            size=1_024_024,
            url="https://example.com/foobar.png?x=4096",
            proxy_url="https://example.com/foobar.png?x=4096",
        )

        async def __aiter__(_):
            yield b"foo"
            yield b"bar"
            yield b"baz"

        web_resource = mock.MagicMock(spec_set=files.WebResourceStream)
        web_resource.__aiter__ = __aiter__

        with mock.patch.object(files, "WebResourceStream", return_value=web_resource):
            async_iterator = attachment.__aiter__()
            assert await async_iterator.__anext__() == b"foo"
            assert await async_iterator.__anext__() == b"bar"
            assert await async_iterator.__anext__() == b"baz"

            with pytest.raises(StopAsyncIteration):
                await async_iterator.__anext__()


class TestReaction:
    def test_deserialize(self, test_reaction_payload, mock_app, test_emoji_payload):
        mock_emoji = mock.MagicMock(emojis.CustomEmoji)

        with _helpers.patch_marshal_attr(
            messages.Reaction, "emoji", return_value=mock_emoji, deserializer=emojis.deserialize_reaction_emoji
        ) as patched_emoji_deserializer:
            reaction_obj = messages.Reaction.deserialize(test_reaction_payload, app=mock_app)
            patched_emoji_deserializer.assert_called_once_with(test_emoji_payload, app=mock_app)

        assert reaction_obj.count == 100
        assert reaction_obj.emoji == mock_emoji
        assert reaction_obj.is_reacted_by_me is True


class TestMessageActivity:
    def test_deserialize(self, test_message_activity_payload, mock_app):
        message_activity_obj = messages.MessageActivity.deserialize(test_message_activity_payload, app=mock_app)

        assert message_activity_obj.type == messages.MessageActivityType.JOIN_REQUEST
        assert message_activity_obj.party_id == "ae488379-351d-4a4f-ad32-2b9b01c91657"


class TestMessageCrosspost:
    def test_deserialize(self, test_message_crosspost_payload, mock_app):
        message_crosspost_obj = messages.MessageCrosspost.deserialize(test_message_crosspost_payload, app=mock_app)

        assert message_crosspost_obj.id == 306588351130107906
        assert message_crosspost_obj.channel_id == 278325129692446722
        assert message_crosspost_obj.guild_id == 278325129692446720


class TestMessage:
    def test_deserialize(
        self,
        test_message_payload,
        test_application_payload,
        test_attachment_payload,
        test_reaction_payload,
        test_user_payload,
        test_member_payload,
        test_message_activity_payload,
        test_message_crosspost_payload,
        mock_app,
    ):
        mock_user = mock.MagicMock(users.User)
        mock_member = mock.MagicMock(guilds.GuildMember)
        mock_datetime = mock.MagicMock(datetime.datetime)
        mock_datetime2 = mock.MagicMock(datetime.datetime)
        mock_emoji = mock.MagicMock(emojis.Emoji)
        mock_app = mock.MagicMock(applications.Application)

        stack = contextlib.ExitStack()
        patched_author_deserializer = stack.enter_context(
            _helpers.patch_marshal_attr(
                messages.Message, "author", deserializer=users.User.deserialize, return_value=mock_user
            )
        )
        patched_member_deserializer = stack.enter_context(
            _helpers.patch_marshal_attr(
                messages.Message, "member", deserializer=guilds.GuildMember.deserialize, return_value=mock_member
            )
        )
        patched_timestamp_deserializer = stack.enter_context(
            _helpers.patch_marshal_attr(
                messages.Message, "timestamp", deserializer=conversions.parse_iso_8601_ts, return_value=mock_datetime,
            )
        )
        patched_edited_timestamp_deserializer = stack.enter_context(
            _helpers.patch_marshal_attr(
                messages.Message,
                "edited_timestamp",
                deserializer=conversions.parse_iso_8601_ts,
                return_value=mock_datetime2,
            )
        )
        patched_application_deserializer = stack.enter_context(
            _helpers.patch_marshal_attr(
                messages.Message,
                "application",
                deserializer=applications.Application.deserialize,
                return_value=mock_app,
            )
        )
        patched_emoji_deserializer = stack.enter_context(
            _helpers.patch_marshal_attr(
                messages.Reaction, "emoji", deserializer=emojis.deserialize_reaction_emoji, return_value=mock_emoji,
            )
        )
        with stack:
            message_obj = messages.Message.deserialize(test_message_payload, app=mock_app)
            patched_emoji_deserializer.assert_called_once_with(test_reaction_payload["emoji"], app=mock_app)
            assert message_obj.reactions == [messages.Reaction.deserialize(test_reaction_payload)]
            assert message_obj.reactions[0]._gateway_consumer is mock_app
            patched_application_deserializer.assert_called_once_with(test_application_payload, app=mock_app)
            patched_edited_timestamp_deserializer.assert_called_once_with("2020-04-21T21:20:16.510000+00:00")
            patched_timestamp_deserializer.assert_called_once_with("2020-03-21T21:20:16.510000+00:00")
            patched_member_deserializer.assert_called_once_with(test_member_payload, app=mock_app)
            patched_author_deserializer.assert_called_once_with(test_user_payload, app=mock_app)

        assert message_obj.id == 123
        assert message_obj.channel_id == 456
        assert message_obj.guild_id == 678
        assert message_obj.author == mock_user
        assert message_obj.member == mock_member
        assert message_obj.content == "some info"
        assert message_obj.timestamp == mock_datetime
        assert message_obj.edited_timestamp == mock_datetime2
        assert message_obj.is_tts is True
        assert message_obj.is_mentioning_everyone is True
        assert message_obj.user_mentions == {5678}
        assert message_obj.role_mentions == {987}
        assert message_obj.channel_mentions == {456}
        assert message_obj.attachments == [messages.Attachment.deserialize(test_attachment_payload)]
        assert message_obj.attachments[0]._gateway_consumer is mock_app
        assert message_obj.embeds == [embeds.Embed.deserialize({})]
        assert message_obj.embeds[0]._gateway_consumer is mock_app
        assert message_obj.is_pinned is True
        assert message_obj.webhook_id == 1234
        assert message_obj.type == messages.MessageType.DEFAULT
        assert message_obj.activity == messages.MessageActivity.deserialize(test_message_activity_payload)
        assert message_obj.activity._gateway_consumer is mock_app
        assert message_obj.application == mock_app
        assert message_obj.message_reference == messages.MessageCrosspost.deserialize(test_message_crosspost_payload)
        assert message_obj.message_reference._gateway_consumer is mock_app
        assert message_obj.flags == messages.MessageFlag.IS_CROSSPOST
        assert message_obj.nonce == "171000788183678976"

    @pytest.fixture()
    def components_impl(self) -> application.Application:
        return mock.MagicMock(application.Application, rest=mock.AsyncMock())

    @pytest.fixture()
    def message_obj(self, components_impl):
        return messages.Message(
            app=components_impl,
            id=123,
            channel_id=44444,
            guild_id=44334,
            author=None,
            member=None,
            content=None,
            timestamp=None,
            edited_timestamp=None,
            is_tts=None,
            is_mentioning_everyone=None,
            user_mentions=[],
            role_mentions=[],
            attachments=[],
            embeds=[],
            is_pinned=None,
            webhook_id=None,
            type=None,
            activity=None,
            application=None,
            message_reference=None,
            flags=None,
            nonce=None,
        )

    @pytest.mark.asyncio
    async def test_fetch_channel(self, message_obj, components_impl):
        mock_channel = mock.MagicMock(channels.GuildChannel)
        components_impl.rest.fetch_channel.return_value = mock_channel
        assert await message_obj.fetch_channel() is mock_channel
        components_impl.rest.fetch_channel.assert_called_once_with(channel=44444)

    @pytest.mark.asyncio
    async def test_edit_without_optionals(self, message_obj, components_impl):
        mock_message = mock.MagicMock(messages.Message)
        components_impl.rest.update_message.return_value = mock_message
        assert await message_obj.edit() is mock_message
        components_impl.rest.update_message.assert_called_once_with(
            message=123,
            channel=44444,
            content=...,
            embed=...,
            mentions_everyone=True,
            user_mentions=True,
            role_mentions=True,
        )

    @pytest.mark.asyncio
    async def test_edit_with_optionals(self, message_obj, components_impl):
        mock_embed = mock.MagicMock(embeds.Embed)
        mock_message = mock.MagicMock(messages.Message)
        components_impl.rest.update_message.return_value = mock_message
        result = await message_obj.edit(
            content="OKOKOKOKOKOKOK",
            embed=mock_embed,
            mentions_everyone=False,
            user_mentions=[123],
            role_mentions=[456],
        )
        assert result is mock_message
        components_impl.rest.update_message.assert_called_once_with(
            message=123,
            channel=44444,
            content="OKOKOKOKOKOKOK",
            embed=mock_embed,
            mentions_everyone=False,
            user_mentions=[123],
            role_mentions=[456],
        )

    @pytest.mark.asyncio
    async def test_safe_edit_without_optionals(self, message_obj, components_impl):
        mock_message = mock.MagicMock(messages.Message)
        components_impl.rest.safe_update_message.return_value = mock_message
        assert await message_obj.safe_edit() is mock_message
        components_impl.rest.safe_update_message.assert_called_once_with(
            message=123,
            channel=44444,
            content=...,
            embed=...,
            mentions_everyone=False,
            user_mentions=False,
            role_mentions=False,
        )

    @pytest.mark.asyncio
    async def test_safe_edit_with_optionals(self, message_obj, components_impl):
        mock_embed = mock.MagicMock(embeds.Embed)
        mock_message = mock.MagicMock(messages.Message)
        components_impl.rest.safe_update_message.return_value = mock_message
        result = await message_obj.safe_edit(
            content="OKOKOKOKOKOKOK", embed=mock_embed, mentions_everyone=True, user_mentions=[123], role_mentions=[456]
        )
        assert result is mock_message
        components_impl.rest.safe_update_message.assert_called_once_with(
            message=123,
            channel=44444,
            content="OKOKOKOKOKOKOK",
            embed=mock_embed,
            mentions_everyone=True,
            user_mentions=[123],
            role_mentions=[456],
        )

    @pytest.mark.asyncio
    async def test_reply_without_optionals(self, message_obj, components_impl):
        mock_message = mock.MagicMock(messages.Message)
        components_impl.rest.create_message.return_value = mock_message
        assert await message_obj.reply() is mock_message
        components_impl.rest.create_message.assert_called_once_with(
            channel=44444,
            content=...,
            nonce=...,
            tts=...,
            files=...,
            embed=...,
            mentions_everyone=True,
            user_mentions=True,
            role_mentions=True,
        )

    @pytest.mark.asyncio
    async def test_reply_with_optionals(self, message_obj, components_impl):
        mock_file = mock.MagicMock(files.BaseStream)
        mock_embed = mock.MagicMock(embeds.Embed)
        mock_message = mock.MagicMock(messages.Message)
        components_impl.rest.create_message.return_value = mock_message
        result = await message_obj.reply(
            content="blah",
            nonce="blah2",
            tts=True,
            files=[mock_file],
            embed=mock_embed,
            mentions_everyone=True,
            user_mentions=[123],
            role_mentions=[444],
        )
        assert result is mock_message
        components_impl.rest.create_message.assert_called_once_with(
            channel=44444,
            content="blah",
            nonce="blah2",
            tts=True,
            files=[mock_file],
            embed=mock_embed,
            mentions_everyone=True,
            user_mentions=[123],
            role_mentions=[444],
        )

    @pytest.mark.asyncio
    async def test_safe_reply_without_optionals(self, message_obj, components_impl):
        mock_message = mock.MagicMock(messages.Message)
        components_impl.rest.safe_create_message.return_value = mock_message
        assert await message_obj.safe_reply() is mock_message
        components_impl.rest.safe_create_message.assert_called_once_with(
            channel=44444,
            content=...,
            nonce=...,
            tts=...,
            files=...,
            embed=...,
            mentions_everyone=False,
            user_mentions=False,
            role_mentions=False,
        )

    @pytest.mark.asyncio
    async def test_safe_reply_with_optionals(self, message_obj, components_impl):
        mock_file = mock.MagicMock(files.BaseStream)
        mock_embed = mock.MagicMock(embeds.Embed)
        mock_message = mock.MagicMock(messages.Message)
        components_impl.rest.safe_create_message.return_value = mock_message
        result = await message_obj.safe_reply(
            content="blah",
            nonce="blah2",
            tts=True,
            files=[mock_file],
            embed=mock_embed,
            mentions_everyone=True,
            user_mentions=[123],
            role_mentions=[444],
        )
        assert result is mock_message
        components_impl.rest.safe_create_message.assert_called_once_with(
            channel=44444,
            content="blah",
            nonce="blah2",
            tts=True,
            files=[mock_file],
            embed=mock_embed,
            mentions_everyone=True,
            user_mentions=[123],
            role_mentions=[444],
        )

    @pytest.mark.asyncio
    async def test_delete(self, message_obj, components_impl):
        assert await message_obj.delete() is None
        components_impl.rest.delete_messages.assert_called_once_with(channel=44444, message=123)

    @pytest.mark.asyncio
    async def test_add_reaction(self, message_obj, components_impl):
        mock_emoji = mock.MagicMock(emojis.Emoji)
        assert await message_obj.add_reaction(mock_emoji) is None
        components_impl.rest.add_reaction.assert_called_once_with(channel=44444, message=123, emoji=mock_emoji)

    @pytest.mark.asyncio
    async def test_add_reaction_without_user(self, message_obj, components_impl):
        mock_emoji = mock.MagicMock(emojis.Emoji)
        assert await message_obj.remove_reaction(mock_emoji) is None
        components_impl.rest.remove_reaction.assert_called_once_with(
            channel=44444, message=123, emoji=mock_emoji, user=None
        )

    @pytest.mark.asyncio
    async def test_add_reaction_with_user(self, message_obj, components_impl):
        mock_emoji = mock.MagicMock(emojis.Emoji)
        user = mock.MagicMock(users.User)
        assert await message_obj.remove_reaction(mock_emoji, user=user) is None
        components_impl.rest.remove_reaction.assert_called_once_with(
            channel=44444, message=123, emoji=mock_emoji, user=user
        )

    @pytest.mark.asyncio
    async def test_remove_all_reactions_without_emoji(self, message_obj, components_impl):
        assert await message_obj.remove_all_reactions() is None
        components_impl.rest.remove_all_reactions.assert_called_once_with(channel=44444, message=123, emoji=None)

    @pytest.mark.asyncio
    async def test_remove_all_reactions_with_emoji(self, message_obj, components_impl):
        mock_emoji = mock.MagicMock(emojis.Emoji)
        assert await message_obj.remove_all_reactions(mock_emoji) is None
        components_impl.rest.remove_all_reactions.assert_called_once_with(channel=44444, message=123, emoji=mock_emoji)
