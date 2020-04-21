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
"""Components and entities that are used to describe Discord gateway events."""

__all__ = [
    "HikariEvent",
    "ExceptionEvent",
    "ConnectedEvent",
    "DisconnectedEvent",
    "StartingEvent",
    "StartedEvent",
    "StoppingEvent",
    "StoppedEvent",
    "ReadyEvent",
    "ResumedEvent",
    "ChannelCreateEvent",
    "ChannelUpdateEvent",
    "ChannelDeleteEvent",
    "ChannelPinUpdateEvent",
    "GuildCreateEvent",
    "GuildUpdateEvent",
    "GuildLeaveEvent",
    "GuildUnavailableEvent",
    "GuildBanAddEvent",
    "GuildBanRemoveEvent",
    "GuildEmojisUpdateEvent",
    "GuildIntegrationsUpdateEvent",
    "GuildMemberAddEvent",
    "GuildMemberUpdateEvent",
    "GuildMemberRemoveEvent",
    "GuildRoleCreateEvent",
    "GuildRoleUpdateEvent",
    "GuildRoleDeleteEvent",
    "InviteCreateEvent",
    "InviteDeleteEvent",
    "MessageCreateEvent",
    "MessageUpdateEvent",
    "MessageDeleteEvent",
    "MessageDeleteBulkEvent",
    "MessageReactionAddEvent",
    "MessageReactionRemoveEvent",
    "MessageReactionRemoveAllEvent",
    "MessageReactionRemoveEmojiEvent",
    "PresenceUpdateEvent",
    "TypingStartEvent",
    "UserUpdateEvent",
    "VoiceStateUpdateEvent",
    "VoiceServerUpdateEvent",
    "WebhookUpdateEvent",
]

import abc
import datetime
import typing

import attr

from hikari import bases
from hikari import channels
from hikari import embeds as _embeds
from hikari import emojis as _emojis
from hikari import guilds
from hikari import intents
from hikari import invites
from hikari import messages
from hikari import applications
from hikari import unset
from hikari import users
from hikari import voices
from hikari.clients import shards
from hikari.internal import assertions
from hikari.internal import conversions
from hikari.internal import marshaller

T_contra = typing.TypeVar("T_contra", contravariant=True)


# Base event, is not deserialized
@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class HikariEvent(bases.HikariEntity, abc.ABC):
    """The base class that all events inherit from."""

    ___required_intents___: typing.ClassVar[intents.Intent]

    def __init_subclass__(cls, *, intent: intents.Intent = intents.Intent(0), **kwargs) -> None:
        super().__init_subclass__()
        assertions.assert_that(isinstance(intent, intents.Intent), "expected an intent type", TypeError)
        cls.___required_intents___ = intent

        if intent:
            new_doc = (cls.__doc__ + "\n\n") if cls.__doc__ is not None else ""
            new_doc += "This event will only fire if the following intents are enabled: "
            new_doc += ", ".join(i.name for i in intents.Intent if i & intent)
            if intent.is_privileged:
                new_doc += "\n\n"
                new_doc += (
                    "This event is privileged, meaning you will need to opt into using one or more "
                    "intents on the Discord Developer Portal."
                )

            cls.__doc__ = new_doc


# Synthetic event, is not deserialized, and is produced by the dispatcher.
@attr.attrs(slots=True, auto_attribs=True)
class ExceptionEvent(HikariEvent):
    """Descriptor for an exception thrown while processing an event."""

    #: The exception that was raised.
    #:
    #: :type: :obj:`~Exception`
    exception: Exception

    #: The event that was being invoked when the exception occurred.
    #:
    #: :type: :obj:`~HikariEvent`
    event: HikariEvent

    #: The event that was being invoked when the exception occurred.
    #:
    #: :type: coroutine function ( :obj:`~HikariEvent` ) -> :obj:`~None`
    callback: typing.Callable[[HikariEvent], typing.Awaitable[None]]


# Synthetic event, is not deserialized
@attr.attrs(slots=True, auto_attribs=True)
class StartingEvent(HikariEvent):
    """Event that is fired before the gateway client starts all shards."""


# Synthetic event, is not deserialized
@attr.attrs(slots=True, auto_attribs=True)
class StartedEvent(HikariEvent):
    """Event that is fired when the gateway client starts all shards."""


# Synthetic event, is not deserialized
@attr.attrs(slots=True, auto_attribs=True)
class StoppingEvent(HikariEvent):
    """Event that is fired when the gateway client is instructed to disconnect all shards."""


# Synthetic event, is not deserialized
@attr.attrs(slots=True, auto_attribs=True)
class StoppedEvent(HikariEvent):
    """Event that is fired when the gateway client has finished disconnecting all shards."""


@attr.s(slots=True, kw_only=True, auto_attribs=True)
class ConnectedEvent(HikariEvent, marshaller.Deserializable):
    """Event invoked each time a shard connects."""

    #: The shard that connected.
    #:
    #: :type: :obj:`~hikari.clients.shard_clients.ShardClient`
    shard: shards.ShardClient


@attr.s(slots=True, kw_only=True, auto_attribs=True)
class DisconnectedEvent(HikariEvent, marshaller.Deserializable):
    """Event invoked each time a shard disconnects."""

    #: The shard that disconnected.
    #:
    #: :type: :obj:`~hikari.clients.shard_clients.ShardClient`
    shard: shards.ShardClient


@attr.s(slots=True, kw_only=True, auto_attribs=True)
class ResumedEvent(HikariEvent):
    """Represents a gateway Resume event."""

    #: The shard that reconnected.
    #:
    #: :type: :obj:`~hikari.clients.shard_clients.ShardClient`
    shard: shards.ShardClient


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class ReadyEvent(HikariEvent, marshaller.Deserializable):
    """Represents the gateway Ready event.

    This is received only when IDENTIFYing with the gateway.
    """

    #: The gateway version this is currently connected to.
    #:
    #: :type: :obj:`~int`
    gateway_version: int = marshaller.attrib(raw_name="v", deserializer=int)

    #: The object of the current bot account this connection is for.
    #:
    #: :type: :obj:`~hikari.users.MyUser`
    my_user: users.MyUser = marshaller.attrib(raw_name="user", deserializer=users.MyUser.deserialize)

    #: A mapping of the guilds this bot is currently in. All guilds will start
    #: off "unavailable".
    #:
    #: :type: :obj:`~typing.Mapping` [ :obj:`~hikari.entities.Snowflake`, :obj:`~hikari.guilds.UnavailableGuild` ]
    unavailable_guilds: typing.Mapping[bases.Snowflake, guilds.UnavailableGuild] = marshaller.attrib(
        raw_name="guilds",
        deserializer=lambda guilds_objs: {g.id: g for g in map(guilds.UnavailableGuild.deserialize, guilds_objs)},
    )

    #: The id of the current gateway session, used for reconnecting.
    #:
    #: :type: :obj:`~str`
    session_id: str = marshaller.attrib(deserializer=str)

    #: Information about the current shard, only provided when IDENTIFYing.
    #:
    #: :type: :obj:`~typing.Tuple` [ :obj:`~int`, :obj:`~int` ], optional
    _shard_information: typing.Optional[typing.Tuple[int, int]] = marshaller.attrib(
        raw_name="shard", deserializer=tuple, if_undefined=None, default=None
    )

    @property
    def shard_id(self) -> typing.Optional[int]:
        """Zero-indexed ID of the current shard.

        This is only available if this ready event was received while IDENTIFYing.
        """
        return self._shard_information[0] if self._shard_information else None

    @property
    def shard_count(self) -> typing.Optional[int]:
        """Total shard count for this bot.

        This is only available if this ready event was received while IDENTIFYing.
        """
        return self._shard_information[1] if self._shard_information else None


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class BaseChannelEvent(
    HikariEvent, bases.UniqueEntity, marshaller.Deserializable, abc.ABC, intent=intents.Intent.GUILDS
):
    """A base object that Channel events will inherit from."""

    #: The channel's type.
    #:
    #: :type: :obj:`~hikari.channels.ChannelType`
    type: channels.ChannelType = marshaller.attrib(deserializer=channels.ChannelType)

    #: The ID of the guild this channel is in, will be :obj:`~None` for DMs.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`, optional
    guild_id: typing.Optional[bases.Snowflake] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_undefined=None, default=None
    )

    #: The sorting position of this channel, will be relative to the
    #: :attr:`parent_id` if set.
    #:
    #: :type: :obj:`~int`, optional
    position: typing.Optional[int] = marshaller.attrib(deserializer=int, if_undefined=None, default=None)

    #: An mapping of the set permission overwrites for this channel, if applicable.
    #:
    #: :type: :obj:`~typing.Mapping` [ :obj:`~hikari.entities.Snowflake`, :obj:`~hikari.channels.PermissionOverwrite` ], optional
    permission_overwrites: typing.Optional[
        typing.Mapping[bases.Snowflake, channels.PermissionOverwrite]
    ] = marshaller.attrib(
        deserializer=lambda overwrites: {o.id: o for o in map(channels.PermissionOverwrite.deserialize, overwrites)},
        if_undefined=None,
        default=None,
    )

    #: The name of this channel, if applicable.
    #:
    #: :type: :obj:`~str`, optional
    name: typing.Optional[str] = marshaller.attrib(deserializer=str, if_undefined=None, default=None)

    #: The topic of this channel, if applicable and set.
    #:
    #: :type: :obj:`~str`, optional
    topic: typing.Optional[str] = marshaller.attrib(deserializer=str, if_undefined=None, if_none=None, default=None)

    #: Whether this channel is nsfw, will be :obj:`~None` if not applicable.
    #:
    #: :type: :obj:`~bool`, optional
    is_nsfw: typing.Optional[bool] = marshaller.attrib(
        raw_name="nsfw", deserializer=bool, if_undefined=None, default=None
    )

    #: The ID of the last message sent, if it's a text type channel.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`, optional
    last_message_id: typing.Optional[bases.Snowflake] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_none=None, if_undefined=None, default=None
    )

    #: The bitrate (in bits) of this channel, if it's a guild voice channel.
    #:
    #: :type: :obj:`~bool`, optional
    bitrate: typing.Optional[int] = marshaller.attrib(deserializer=int, if_undefined=None, default=None)

    #: The user limit for this channel if it's a guild voice channel.
    #:
    #: :type: :obj:`~bool`, optional
    user_limit: typing.Optional[int] = marshaller.attrib(deserializer=int, if_undefined=None, default=None)

    #: The rate limit a user has to wait before sending another message in this
    #: channel, if it's a guild text like channel.
    #:
    #: :type: :obj:`~datetime.timedelta`, optional
    rate_limit_per_user: typing.Optional[datetime.timedelta] = marshaller.attrib(
        deserializer=lambda delta: datetime.timedelta(seconds=delta), if_undefined=None, default=None
    )

    #: A mapping of this channel's recipient users, if it's a DM or group DM.
    #:
    #: :type: :obj:`~typing.Mapping` [ :obj:`~hikari.entities.Snowflake`, :obj:`~hikari.users.User` ], optional
    recipients: typing.Optional[typing.Mapping[bases.Snowflake, users.User]] = marshaller.attrib(
        deserializer=lambda recipients: {user.id: user for user in map(users.User.deserialize, recipients)},
        if_undefined=None,
        default=None,
    )

    #: The hash of this channel's icon, if it's a group DM channel and is set.
    #:
    #: :type: :obj:`~str`, optional
    icon_hash: typing.Optional[str] = marshaller.attrib(
        raw_name="icon", deserializer=str, if_undefined=None, if_none=None, default=None
    )

    #: The ID of this channel's creator, if it's a DM channel.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`, optional
    owner_id: typing.Optional[bases.Snowflake] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_undefined=None, default=None
    )

    #: The ID of the application that created the group DM, if it's a
    #: bot based group DM.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`, optional
    application_id: typing.Optional[bases.Snowflake] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_undefined=None, default=None
    )

    #: The ID of this channels's parent category within guild, if set.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`, optional
    parent_id: typing.Optional[bases.Snowflake] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_undefined=None, if_none=None, default=None
    )

    #: The datetime of when the last message was pinned in this channel,
    #: if set and applicable.
    #:
    #: :type: :obj:`~datetime.datetime`, optional
    last_pin_timestamp: typing.Optional[datetime.datetime] = marshaller.attrib(
        deserializer=conversions.parse_iso_8601_ts, if_undefined=None, default=None
    )


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class ChannelCreateEvent(BaseChannelEvent, intent=intents.Intent.GUILDS):
    """Represents Channel Create gateway events.

    Will be sent when a guild channel is created and before all Create Message
    events that originate from a DM channel.
    """


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class ChannelUpdateEvent(BaseChannelEvent, intent=intents.Intent.GUILDS):
    """Represents Channel Update gateway events."""


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class ChannelDeleteEvent(BaseChannelEvent, intent=intents.Intent.GUILDS):
    """Represents Channel Delete gateway events."""


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class ChannelPinUpdateEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILDS):
    """Used to represent the Channel Pins Update gateway event.

    Sent when a message is pinned or unpinned in a channel but not
    when a pinned message is deleted.
    """

    #: The ID of the guild where this event happened.
    #: Will be :obj:`~None` if this happened in a DM channel.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`, optional
    guild_id: typing.Optional[bases.Snowflake] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_undefined=None, default=None
    )

    #: The ID of the channel where the message was pinned or unpinned.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    channel_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The datetime of when the most recent message was pinned in this channel.
    #: Will be :obj:`~None` if there are no messages pinned after this change.
    #:
    #: :type: :obj:`~datetime.datetime`, optional
    last_pin_timestamp: typing.Optional[datetime.datetime] = marshaller.attrib(
        deserializer=conversions.parse_iso_8601_ts, if_undefined=None, default=None
    )


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class GuildCreateEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILDS):
    """Used to represent Guild Create gateway events.

    Will be received when the bot joins a guild, and when a guild becomes
    available to a guild (either due to outage or at startup).
    """


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class GuildUpdateEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILDS):
    """Used to represent Guild Update gateway events."""


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class GuildLeaveEvent(HikariEvent, bases.UniqueEntity, marshaller.Deserializable, intent=intents.Intent.GUILDS):
    """Fired when the current user leaves the guild or is kicked/banned from it.

    Notes
    -----
    This is fired based on Discord's Guild Delete gateway event.
    """


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class GuildUnavailableEvent(HikariEvent, bases.UniqueEntity, marshaller.Deserializable, intent=intents.Intent.GUILDS):
    """Fired when a guild becomes temporarily unavailable due to an outage.

    Notes
    -----
    This is fired based on Discord's Guild Delete gateway event.
    """


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class BaseGuildBanEvent(HikariEvent, marshaller.Deserializable, abc.ABC, intent=intents.Intent.GUILD_BANS):
    """A base object that guild ban events will inherit from."""

    #: The ID of the guild this ban is in.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    guild_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The object of the user this ban targets.
    #:
    #: :type: :obj:`~hikari.users.User`
    user: users.User = marshaller.attrib(deserializer=users.User.deserialize)


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class GuildBanAddEvent(BaseGuildBanEvent, intent=intents.Intent.GUILD_BANS):
    """Used to represent a Guild Ban Add gateway event."""


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class GuildBanRemoveEvent(BaseGuildBanEvent, intent=intents.Intent.GUILD_BANS):
    """Used to represent a Guild Ban Remove gateway event."""


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class GuildEmojisUpdateEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILD_EMOJIS):
    """Represents a Guild Emoji Update gateway event."""

    #: The ID of the guild this emoji was updated in.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    guild_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The updated mapping of emojis by their ID.
    #:
    #: :type: :obj:`~typing.Mapping` [ :obj:`~hikari.entities.Snowflake`, :obj:`~hikari.emojis.GuildEmoji` ]
    emojis: typing.Mapping[bases.Snowflake, _emojis.GuildEmoji] = marshaller.attrib(
        deserializer=lambda ems: {emoji.id: emoji for emoji in map(_emojis.GuildEmoji.deserialize, ems)}
    )


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class GuildIntegrationsUpdateEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILD_INTEGRATIONS):
    """Used to represent Guild Integration Update gateway events."""

    #: The ID of the guild the integration was updated in.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    guild_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class GuildMemberAddEvent(HikariEvent, guilds.GuildMember, intent=intents.Intent.GUILD_MEMBERS):
    """Used to represent a Guild Member Add gateway event."""

    #: The ID of the guild where this member was added.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    guild_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class GuildMemberUpdateEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILD_MEMBERS):
    """Used to represent a Guild Member Update gateway event.

    Sent when a guild member or their inner user object is updated.
    """

    #: The ID of the guild this member was updated in.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    guild_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: A sequence of the IDs of the member's current roles.
    #:
    #: :type: :obj:`~typing.Sequence` [ :obj:`~hikari.entities.Snowflake` ]
    role_ids: typing.Sequence[bases.Snowflake] = marshaller.attrib(
        raw_name="roles", deserializer=lambda role_ids: [bases.Snowflake.deserialize(rid) for rid in role_ids],
    )

    #: The object of the user who was updated.
    #:
    #:  :type: :obj:`~hikari.users.User`
    user: users.User = marshaller.attrib(deserializer=users.User.deserialize)

    #: This member's nickname. When set to :obj:`~None`, this has been removed
    #: and when set to :obj:`~hikari.unset.UNSET` this hasn't been acted on.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~str`, :obj:`~hikari.unset.UNSET` ], optional
    nickname: typing.Union[None, str, unset.Unset] = marshaller.attrib(
        raw_name="nick", deserializer=str, if_none=None, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: The datetime of when this member started "boosting" this guild.
    #: Will be :obj:`~None` if they aren't boosting.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~datetime.datetime`, :obj:`~hikari.unset.UNSET` ], optional
    premium_since: typing.Union[None, datetime.datetime, unset.Unset] = marshaller.attrib(
        deserializer=conversions.parse_iso_8601_ts, if_none=None, if_undefined=unset.Unset, default=unset.UNSET
    )


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class GuildMemberRemoveEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILD_MEMBERS):
    """Used to represent Guild Member Remove gateway events.

    Sent when a member is kicked, banned or leaves a guild.
    """

    #: The ID of the guild this user was removed from.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    guild_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The object of the user who was removed from this guild.
    #:
    #:  :type: :obj:`~hikari.users.User`
    user: users.User = marshaller.attrib(deserializer=users.User.deserialize)


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class GuildRoleCreateEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILDS):
    """Used to represent a Guild Role Create gateway event."""

    #: The ID of the guild where this role was created.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    guild_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The object of the role that was created.
    #:
    #: :type: :obj:`~hikari.guilds.GuildRole`
    role: guilds.GuildRole = marshaller.attrib(deserializer=guilds.GuildRole.deserialize)


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class GuildRoleUpdateEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILDS):
    """Used to represent a Guild Role Create gateway event."""

    #: The ID of the guild where this role was updated.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    guild_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The updated role object.
    #:
    #: :type: :obj:`~hikari.guilds.GuildRole`
    role: guilds.GuildRole = marshaller.attrib(deserializer=guilds.GuildRole.deserialize)


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class GuildRoleDeleteEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILDS):
    """Represents a gateway Guild Role Delete Event."""

    #: The ID of the guild where this role is being deleted.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    guild_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The ID of the role being deleted.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    role_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class InviteCreateEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILD_INVITES):
    """Represents a gateway Invite Create event."""

    #: The ID of the channel this invite targets.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    channel_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The code that identifies this invite
    #:
    #: :type: :obj:`~str`
    code: str = marshaller.attrib(deserializer=str)

    #: The datetime of when this invite was created.
    #:
    #: :type: :obj:`~datetime.datetime`
    created_at: datetime.datetime = marshaller.attrib(deserializer=conversions.parse_iso_8601_ts)

    #: The ID of the guild this invite was created in, if applicable.
    #: Will be :obj:`~None` for group DM invites.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`, optional
    guild_id: typing.Optional[bases.Snowflake] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_undefined=None, default=None
    )

    #: The object of the user who created this invite, if applicable.
    #:
    #: :type: :obj:`~hikari.users.User`, optional
    inviter: typing.Optional[users.User] = marshaller.attrib(
        deserializer=users.User.deserialize, if_undefined=None, default=None
    )

    #: The timedelta of how long this invite will be valid for.
    #: If set to :obj:`~None` then this is unlimited.
    #:
    #: :type: :obj:`~datetime.timedelta`, optional
    max_age: typing.Optional[datetime.timedelta] = marshaller.attrib(
        deserializer=lambda age: datetime.timedelta(seconds=age) if age > 0 else None,
    )

    #: The limit for how many times this invite can be used before it expires.
    #: If set to ``0``, or infinity (``float("inf")``) then this is unlimited.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~int`, :obj:`~float` ( ``"inf"`` ) ]
    max_uses: typing.Union[int, float] = marshaller.attrib(deserializer=lambda count: count or float("inf"))

    #: The object of the user who this invite targets, if set.
    #:
    #: :type: :obj:`~hikari.users.User`, optional
    target_user: typing.Optional[users.User] = marshaller.attrib(
        deserializer=users.User.deserialize, if_undefined=None, default=None
    )

    #: The type of user target this invite is, if applicable.
    #:
    #: :type: :obj:`~hikari.invites.TargetUserType`, optional
    target_user_type: typing.Optional[invites.TargetUserType] = marshaller.attrib(
        deserializer=invites.TargetUserType, if_undefined=None, default=None
    )

    #: Whether this invite grants temporary membership.
    #:
    #: :type: :obj:`~bool`
    is_temporary: bool = marshaller.attrib(raw_name="temporary", deserializer=bool)

    #: The amount of times this invite has been used.
    #:
    #: :type: :obj:`~int`
    uses: int = marshaller.attrib(deserializer=int)


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class InviteDeleteEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILD_INVITES):
    """Used to represent Invite Delete gateway events.

    Sent when an invite is deleted for a channel we can access.
    """

    #: The ID of the channel this ID was attached to
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    channel_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The code of this invite.
    #:
    #: :type: :obj:`~str`
    code: str = marshaller.attrib(deserializer=str)

    #: The ID of the guild this invite was deleted in.
    #: This will be :obj:`~None` if this invite belonged to a DM channel.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`, optional
    guild_id: typing.Optional[bases.Snowflake] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_undefined=None, default=None
    )


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class MessageCreateEvent(HikariEvent, messages.Message, intent=intents.Intent.GUILD_MESSAGES):
    """Used to represent Message Create gateway events."""


# This is an arbitrarily partial version of `messages.Message`
@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class MessageUpdateEvent(
    HikariEvent, bases.UniqueEntity, marshaller.Deserializable, intent=intents.Intent.GUILD_MESSAGES
):
    """Represents Message Update gateway events.

    Note
    ----
    All fields on this model except :attr:`channel_id` and :obj:`~`HikariEvent.id`` may be
    set to :obj:`~hikari.unset.UNSET` (a singleton defined in
    ``hikari.entities``) if we have not received information about their
    state from Discord alongside field nullability.
    """

    #: The ID of the channel that the message was sent in.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    channel_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The ID of the guild that the message was sent in.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~hikari.entities.Snowflake`, :obj:`~hikari.unset.UNSET` ]
    guild_id: typing.Union[bases.Snowflake, unset.Unset] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: The author of this message.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~hikari.users.User`, :obj:`~hikari.unset.UNSET` ]
    author: typing.Union[users.User, unset.Unset] = marshaller.attrib(
        deserializer=users.User.deserialize, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: The member properties for the message's author.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~hikari.guilds.GuildMember`, :obj:`~hikari.unset.UNSET` ]
    member: typing.Union[guilds.GuildMember, unset.Unset] = marshaller.attrib(
        deserializer=guilds.GuildMember.deserialize, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: The content of the message.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~str`, :obj:`~hikari.unset.UNSET` ]
    content: typing.Union[str, unset.Unset] = marshaller.attrib(
        deserializer=str, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: The timestamp that the message was sent at.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~datetime.datetime`, :obj:`~hikari.unset.UNSET` ]
    timestamp: typing.Union[datetime.datetime, unset.Unset] = marshaller.attrib(
        deserializer=conversions.parse_iso_8601_ts, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: The timestamp that the message was last edited at, or :obj:`~None` if
    #: it wasn't ever edited.
    #:
    #: :type: :obj:`~typing.Union` [  :obj:`~datetime.datetime`, :obj:`~hikari.unset.UNSET` ], optional
    edited_timestamp: typing.Union[datetime.datetime, unset.Unset, None] = marshaller.attrib(
        deserializer=conversions.parse_iso_8601_ts, if_none=None, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: Whether the message is a TTS message.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~bool`, :obj:`~hikari.unset.UNSET` ]
    is_tts: typing.Union[bool, unset.Unset] = marshaller.attrib(
        raw_name="tts", deserializer=bool, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: Whether the message mentions ``@everyone`` or ``@here``.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~bool`, :obj:`~hikari.unset.UNSET` ]
    is_mentioning_everyone: typing.Union[bool, unset.Unset] = marshaller.attrib(
        raw_name="mention_everyone", deserializer=bool, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: The users the message mentions.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~typing.Set` [ :obj:`~hikari.entities.Snowflake` ], :obj:`~hikari.unset.UNSET` ]
    user_mentions: typing.Union[typing.Set[bases.Snowflake], unset.Unset] = marshaller.attrib(
        raw_name="mentions",
        deserializer=lambda user_mentions: {bases.Snowflake.deserialize(u["id"]) for u in user_mentions},
        if_undefined=unset.Unset,
        default=unset.UNSET,
    )

    #: The roles the message mentions.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~typing.Set` [ :obj:`~hikari.entities.Snowflake` ], :obj:`~hikari.unset.UNSET` ]
    role_mentions: typing.Union[typing.Set[bases.Snowflake], unset.Unset] = marshaller.attrib(
        raw_name="mention_roles",
        deserializer=lambda role_mentions: {bases.Snowflake.deserialize(r) for r in role_mentions},
        if_undefined=unset.Unset,
        default=unset.UNSET,
    )

    #: The channels the message mentions.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~typing.Set` [ :obj:`~hikari.entities.Snowflake` ], :obj:`~hikari.unset.UNSET` ]
    channel_mentions: typing.Union[typing.Set[bases.Snowflake], unset.Unset] = marshaller.attrib(
        raw_name="mention_channels",
        deserializer=lambda channel_mentions: {bases.Snowflake.deserialize(c["id"]) for c in channel_mentions},
        if_undefined=unset.Unset,
        default=unset.UNSET,
    )

    #: The message attachments.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~typing.Sequence` [ :obj:`~hikari.messages.Attachment` ], :obj:`~hikari.unset.UNSET` ]
    attachments: typing.Union[typing.Sequence[messages.Attachment], unset.Unset] = marshaller.attrib(
        deserializer=lambda attachments: [messages.Attachment.deserialize(a) for a in attachments],
        if_undefined=unset.Unset,
        default=unset.UNSET,
    )

    #: The message's embeds.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~typing.Sequence` [ :obj:`~hikari.embeds.Embed` ], :obj:`~hikari.unset.UNSET` ]
    embeds: typing.Union[typing.Sequence[_embeds.Embed], unset.Unset] = marshaller.attrib(
        deserializer=lambda embed_objs: [_embeds.Embed.deserialize(e) for e in embed_objs],
        if_undefined=unset.Unset,
        default=unset.UNSET,
    )

    #: The message's reactions.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~typing.Sequence` [ :obj:`~hikari.messages.Reaction` ], :obj:`~hikari.unset.UNSET` ]
    reactions: typing.Union[typing.Sequence[messages.Reaction], unset.Unset] = marshaller.attrib(
        deserializer=lambda reactions: [messages.Reaction.deserialize(r) for r in reactions],
        if_undefined=unset.Unset,
        default=unset.UNSET,
    )

    #: Whether the message is pinned.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~bool`, :obj:`~hikari.unset.UNSET` ]
    is_pinned: typing.Union[bool, unset.Unset] = marshaller.attrib(
        raw_name="pinned", deserializer=bool, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: If the message was generated by a webhook, the webhook's id.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~hikari.entities.Snowflake`, :obj:`~hikari.unset.UNSET` ]
    webhook_id: typing.Union[bases.Snowflake, unset.Unset] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: The message's type.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~hikari.messages.MessageType`, :obj:`~hikari.unset.UNSET` ]
    type: typing.Union[messages.MessageType, unset.Unset] = marshaller.attrib(
        deserializer=messages.MessageType, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: The message's activity.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~hikari.messages.MessageActivity`, :obj:`~hikari.unset.UNSET` ]
    activity: typing.Union[messages.MessageActivity, unset.Unset] = marshaller.attrib(
        deserializer=messages.MessageActivity.deserialize, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: The message's application.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~hikari.oauth2.Application`, :obj:`~hikari.unset.UNSET` ]
    application: typing.Optional[applications.Application] = marshaller.attrib(
        deserializer=applications.Application.deserialize, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: The message's crossposted reference data.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~hikari.messages.MessageCrosspost`, :obj:`~hikari.unset.UNSET` ]
    message_reference: typing.Union[messages.MessageCrosspost, unset.Unset] = marshaller.attrib(
        deserializer=messages.MessageCrosspost.deserialize, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: The message's flags.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~hikari.messages.MessageFlag`, :obj:`~hikari.unset.UNSET` ]
    flags: typing.Union[messages.MessageFlag, unset.Unset] = marshaller.attrib(
        deserializer=messages.MessageFlag, if_undefined=unset.Unset, default=unset.UNSET
    )

    #: The message nonce. This is a string used for validating
    #: a message was sent.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~hikari.messages.MessageFlag`, :obj:`~hikari.unset.UNSET` ]
    nonce: typing.Union[str, unset.Unset] = marshaller.attrib(
        deserializer=str, if_undefined=unset.Unset, default=unset.UNSET
    )


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class MessageDeleteEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILD_MESSAGES):
    """Used to represent Message Delete gateway events.

    Sent when a message is deleted in a channel we have access to.
    """

    #: The ID of the channel where this message was deleted.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    channel_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The ID of the guild where this message was deleted.
    #: Will be :obj:`~None` if this message was deleted in a DM channel.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`, optional
    guild_id: typing.Optional[bases.Snowflake] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_undefined=None, default=None
    )
    #: The ID of the message that was deleted.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    message_id: bases.Snowflake = marshaller.attrib(raw_name="id", deserializer=bases.Snowflake.deserialize)


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class MessageDeleteBulkEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILD_MESSAGES):
    """Used to represent Message Bulk Delete gateway events.

    Sent when multiple messages are deleted in a channel at once.
    """

    #: The ID of the channel these messages have been deleted in.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    channel_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The ID of the channel these messages have been deleted in.
    #: Will be :obj:`~None` if these messages were bulk deleted in a DM channel.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`, optional
    guild_id: typing.Optional[bases.Snowflake] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_none=None
    )

    #: A collection of the IDs of the messages that were deleted.
    #:
    #: :type: :obj:`~typing.Set` [ :obj:`~hikari.entities.Snowflake` ]
    message_ids: typing.Set[bases.Snowflake] = marshaller.attrib(
        raw_name="ids", deserializer=lambda msgs: {bases.Snowflake.deserialize(m) for m in msgs}
    )


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class MessageReactionAddEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILD_MESSAGE_REACTIONS):
    """Used to represent Message Reaction Add gateway events."""

    #: The ID of the user adding the reaction.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    user_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The ID of the channel where this reaction is being added.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    channel_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The ID of the message this reaction is being added to.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    message_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The ID of the guild where this reaction is being added, unless this is
    #: happening in a DM channel.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`, optional
    guild_id: typing.Optional[bases.Snowflake] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_undefined=None, default=None
    )

    #: The member object of the user who's adding this reaction, if this is
    #: occurring in a guild.
    #:
    #: :type: :obj:`~hikari.guilds.GuildMember`, optional
    member: typing.Optional[guilds.GuildMember] = marshaller.attrib(
        deserializer=guilds.GuildMember.deserialize, if_undefined=None, default=None
    )

    #: The object of the emoji being added.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~hikari.emojis.UnknownEmoji`, :obj:`~hikari.emojis.UnicodeEmoji` ]
    emoji: typing.Union[_emojis.UnknownEmoji, _emojis.UnicodeEmoji] = marshaller.attrib(
        deserializer=_emojis.deserialize_reaction_emoji,
    )


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class MessageReactionRemoveEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILD_MESSAGE_REACTIONS):
    """Used to represent Message Reaction Remove gateway events."""

    #: The ID of the user who is removing their reaction.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    user_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The ID of the channel where this reaction is being removed.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    channel_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The ID of the message this reaction is being removed from.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    message_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The ID of the guild where this reaction is being removed, unless this is
    #: happening in a DM channel.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`, optional
    guild_id: typing.Optional[bases.Snowflake] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_undefined=None, default=None
    )

    #: The object of the emoji being removed.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~hikari.emojis.UnknownEmoji`, :obj:`~hikari.emojis.UnicodeEmoji` ]
    emoji: typing.Union[_emojis.UnicodeEmoji, _emojis.UnknownEmoji] = marshaller.attrib(
        deserializer=_emojis.deserialize_reaction_emoji,
    )


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class MessageReactionRemoveAllEvent(
    HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILD_MESSAGE_REACTIONS
):
    """Used to represent Message Reaction Remove All gateway events.

    Sent when all the reactions are removed from a message, regardless of emoji.
    """

    #: The ID of the channel where the targeted message is.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    channel_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The ID of the message all reactions are being removed from.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    message_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The ID of the guild where the targeted message is, if applicable.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    guild_id: typing.Optional[bases.Snowflake] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_undefined=None, default=None
    )


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class MessageReactionRemoveEmojiEvent(
    HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILD_MESSAGE_REACTIONS
):
    """Represents Message Reaction Remove Emoji events.

    Sent when all the reactions for a single emoji are removed from a message.
    """

    #: The ID of the channel where the targeted message is.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    channel_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The ID of the guild where the targeted message is, if applicable.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    guild_id: typing.Optional[bases.Snowflake] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_undefined=None, default=None
    )

    #: The ID of the message the reactions are being removed from.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    message_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The object of the emoji that's being removed.
    #:
    #: :type: :obj:`~typing.Union` [ :obj:`~hikari.emojis.UnknownEmoji`, :obj:`~hikari.emojis.UnicodeEmoji` ]
    emoji: typing.Union[_emojis.UnicodeEmoji, _emojis.UnknownEmoji] = marshaller.attrib(
        deserializer=_emojis.deserialize_reaction_emoji,
    )


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class PresenceUpdateEvent(HikariEvent, guilds.GuildMemberPresence, intent=intents.Intent.GUILD_PRESENCES):
    """Used to represent Presence Update gateway events.

    Sent when a guild member changes their presence.
    """


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class TypingStartEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILD_MESSAGE_TYPING):
    """Used to represent typing start gateway events.

    Received when a user or bot starts "typing" in a channel.
    """

    #: The ID of the channel this typing event is occurring in.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    channel_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The ID of the guild this typing event is occurring in.
    #: Will be :obj:`~None` if this event is happening in a DM channel.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`, optional
    guild_id: typing.Optional[bases.Snowflake] = marshaller.attrib(
        deserializer=bases.Snowflake.deserialize, if_undefined=None, default=None
    )

    #: The ID of the user who triggered this typing event.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    user_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The datetime of when this typing event started.
    #:
    #: :type: :obj:`~datetime.datetime`
    timestamp: datetime.datetime = marshaller.attrib(
        deserializer=lambda date: datetime.datetime.fromtimestamp(date, datetime.timezone.utc)
    )

    #: The member object of the user who triggered this typing event,
    #: if this was triggered in a guild.
    #:
    #: :type: :obj:`~hikari.guilds.GuildMember`, optional
    member: typing.Optional[guilds.GuildMember] = marshaller.attrib(
        deserializer=guilds.GuildMember.deserialize, if_undefined=None, default=None
    )


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class UserUpdateEvent(HikariEvent, users.MyUser):
    """Used to represent User Update gateway events.

    Sent when the current user is updated.
    """


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class VoiceStateUpdateEvent(HikariEvent, voices.VoiceState, intent=intents.Intent.GUILD_VOICE_STATES):
    """Used to represent voice state update gateway events.

    Sent when a user joins, leaves or moves voice channel(s).
    """


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class VoiceServerUpdateEvent(HikariEvent, marshaller.Deserializable):
    """Used to represent voice server update gateway events.

    Sent when initially connecting to voice and when the current voice instance
    falls over to a new server.
    """

    #: The voice connection's token
    #:
    #: :type: :obj:`~str`
    token: str = marshaller.attrib(deserializer=str)

    #: The ID of the guild this voice server update is for
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    guild_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The uri for this voice server host.
    #:
    #: :type: :obj:`~str`
    endpoint: str = marshaller.attrib(deserializer=str)


@marshaller.marshallable()
@attr.s(slots=True, kw_only=True)
class WebhookUpdateEvent(HikariEvent, marshaller.Deserializable, intent=intents.Intent.GUILD_MESSAGE_TYPING):
    """Used to represent webhook update gateway events.

    Sent when a webhook is updated, created or deleted in a guild.
    """

    #: The ID of the guild this webhook is being updated in.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    guild_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)

    #: The ID of the channel this webhook is being updated in.
    #:
    #: :type: :obj:`~hikari.entities.Snowflake`
    channel_id: bases.Snowflake = marshaller.attrib(deserializer=bases.Snowflake.deserialize)
