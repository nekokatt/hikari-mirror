# -*- coding: utf-8 -*-
# cython: language_level=3
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
"""Application and entities that are used to describe guilds on Discord."""

from __future__ import annotations

__all__: typing.Final[typing.List[str]] = [
    "Guild",
    "RESTGuild",
    "GatewayGuild",
    "GuildWidget",
    "Role",
    "GuildFeature",
    "GuildFeatureish",
    "GuildSystemChannelFlag",
    "GuildMessageNotificationsLevel",
    "GuildExplicitContentFilterLevel",
    "GuildMFALevel",
    "GuildVerificationLevel",
    "GuildPremiumTier",
    "GuildPreview",
    "Member",
    "Integration",
    "GuildMemberBan",
    "IntegrationAccount",
    "IntegrationExpireBehaviour",
    "PartialGuild",
    "PartialIntegration",
    "PartialRole",
    "UnavailableGuild",
]

import abc
import enum
import typing

import attr

from hikari.models import users
from hikari.utilities import constants
from hikari.utilities import files
from hikari.utilities import flag
from hikari.utilities import iterators
from hikari.utilities import routes
from hikari.utilities import snowflake

if typing.TYPE_CHECKING:
    import datetime

    from hikari.api import rest as rest_app
    from hikari.models import channels as channels_
    from hikari.models import colors
    from hikari.models import colours
    from hikari.models import emojis as emojis_
    from hikari.models import permissions as permissions_
    from hikari.models import presences as presences_
    from hikari.utilities import undefined


@enum.unique
@typing.final
class GuildExplicitContentFilterLevel(enum.IntEnum):
    """Represents the explicit content filter setting for a guild."""

    DISABLED = 0
    """No explicit content filter."""

    MEMBERS_WITHOUT_ROLES = 1
    """Filter posts from anyone without a role."""

    ALL_MEMBERS = 2
    """Filter all posts."""

    def __str__(self) -> str:
        return self.name


@enum.unique
@typing.final
class GuildFeature(str, enum.Enum):
    """Features that a guild can provide."""

    ANIMATED_ICON = "ANIMATED_ICON"
    """Guild has access to set an animated guild icon."""

    BANNER = "BANNER"
    """Guild has access to set a guild banner image."""

    COMMERCE = "COMMERCE"
    """Guild has access to use commerce features (i.e. create store channels)."""

    COMMUNITY = "COMMUNITY"
    """Guild has community features enabled."""

    DISCOVERABLE = "DISCOVERABLE"
    """Guild is able to be discovered in the directory."""

    FEATURABLE = "FEATURABLE"
    """Guild is able to be featured in the directory."""

    INVITE_SPLASH = "INVITE_SPLASH"
    """Guild has access to set an invite splash background."""

    MORE_EMOJI = "MORE_EMOJI"
    """More emojis can be hosted in this guild than normal."""

    NEWS = "NEWS"
    """Guild has access to create news channels."""

    LURKABLE = "LURKABLE"
    """People can view channels in this guild without joining."""

    PARTNERED = "PARTNERED"
    """Guild is partnered."""

    PUBLIC = "PUBLIC"
    """Guild is public, go figure."""

    PUBLIC_DISABLED = "PUBLIC_DISABLED"
    """Guild cannot be public. Who would have guessed?"""

    VANITY_URL = "VANITY_URL"
    """Guild has access to set a vanity URL."""

    VERIFIED = "VERIFIED"
    """Guild is verified."""

    VIP_REGIONS = "VIP_REGIONS"
    """Guild has access to set 384kbps bitrate in voice.

    Previously gave access to VIP voice servers.
    """

    WELCOME_SCREEN_ENABLED = "WELCOME_SCREEN_ENABLED"
    """Guild has enabled the welcome screen."""

    def __str__(self) -> str:
        return self.name


GuildFeatureish = typing.Union[str, GuildFeature]
"""Type hint for possible guild features.

Generally these will be of type `GuildFeature`, but undocumented or new
fields may just be `builtins.str` until they are documented and amended to the
library.
"""


@enum.unique
@typing.final
class GuildMessageNotificationsLevel(enum.IntEnum):
    """Represents the default notification level for new messages in a guild."""

    ALL_MESSAGES = 0
    """Notify users when any message is sent."""

    ONLY_MENTIONS = 1
    """Only notify users when they are @mentioned."""

    def __str__(self) -> str:
        return self.name


@enum.unique
@typing.final
class GuildMFALevel(enum.IntEnum):
    """Represents the multi-factor authorization requirement for a guild."""

    NONE = 0
    """No MFA requirement."""

    ELEVATED = 1
    """MFA requirement."""

    def __str__(self) -> str:
        return self.name


@enum.unique
@typing.final
class GuildPremiumTier(enum.IntEnum):
    """Tier for Discord Nitro boosting in a guild."""

    NONE = 0
    """No Nitro boost level."""

    TIER_1 = 1
    """Level 1 Nitro boost."""

    TIER_2 = 2
    """Level 2 Nitro boost."""

    TIER_3 = 3
    """Level 3 Nitro boost."""

    def __str__(self) -> str:
        return self.name


@enum.unique
@typing.final
class GuildSystemChannelFlag(flag.Flag):
    """Defines which features are suppressed in the system channel."""

    SUPPRESS_USER_JOIN = 1 << 0
    """Display a message about new users joining."""

    SUPPRESS_PREMIUM_SUBSCRIPTION = 1 << 1
    """Display a message when the guild is Nitro boosted."""


@enum.unique
@typing.final
class GuildVerificationLevel(enum.IntEnum):
    """Represents the level of verification of a guild."""

    NONE = 0
    """Unrestricted."""

    LOW = 1
    """Must have a verified email on their account."""

    MEDIUM = 2
    """Must have been registered on Discord for more than 5 minutes."""

    HIGH = 3
    """Must also be a member of the guild for longer than 10 minutes."""

    VERY_HIGH = 4
    """Must have a verified phone number."""

    def __str__(self) -> str:
        return self.name


@attr.s(eq=True, hash=False, init=False, kw_only=True, slots=True, weakref_slot=False)
class GuildWidget:
    """Represents a guild embed."""

    app: rest_app.IRESTApp = attr.ib(default=None, repr=False, eq=False, hash=False)
    """The client application that models may use for procedures."""

    channel_id: typing.Optional[snowflake.Snowflake] = attr.ib(repr=True)
    """The ID of the channel the invite for this embed targets, if enabled."""

    is_enabled: bool = attr.ib(repr=True)
    """Whether this embed is enabled."""


@attr.s(eq=True, hash=True, init=False, kw_only=True, slots=True, weakref_slot=False)
class Member(users.User):
    """Used to represent a guild bound member."""

    guild_id: snowflake.Snowflake = attr.ib(eq=True, hash=True, repr=True)
    """The ID of the guild this member belongs to."""

    # This is technically optional, since UPDATE MEMBER and MESSAGE CREATE
    # events do not inject the user into the member payload, but specify it
    # separately. However, to get around this inconsistency, we force the
    # entity factory to always provide the user object in these cases, so we
    # can assume this is always set, and thus we are always able to get info
    # such as the ID of the user this member represents.
    # TODO: make member generic on this field (e.g. Member[PartialUser], Member[UserImpl], Member[OwnUser], etc)?
    user: users.UserImpl = attr.ib(eq=True, hash=True, repr=True)
    """This member's corresponding user object."""

    nickname: undefined.UndefinedNoneOr[str] = attr.ib(
        eq=False, hash=False, repr=True,
    )
    """This member's nickname.

    This will be `builtins.None` if not set.

    On member update events, this may not be included at all.
    In this case, this will be undefined.
    """

    role_ids: typing.Sequence[snowflake.Snowflake] = attr.ib(eq=False, hash=False, repr=False)
    """A sequence of the IDs of the member's current roles."""

    joined_at: undefined.UndefinedOr[datetime.datetime] = attr.ib(eq=False, hash=False, repr=False)
    """The datetime of when this member joined the guild they belong to."""

    premium_since: undefined.UndefinedNoneOr[datetime.datetime] = attr.ib(eq=False, hash=False, repr=False)
    """The datetime of when this member started "boosting" this guild.

    This will be `builtins.None` if they aren't boosting and
    `hikari.utilities.undefined.UndefinedType` if their boosting status is
    unknown.
    """

    is_deaf: undefined.UndefinedOr[bool] = attr.ib(eq=False, hash=False, repr=False)
    """`builtins.True` if this member is deafened in the current voice channel.

    This will be `hikari.utilities.undefined.UndefinedType if it's state is
    unknown.
    """

    is_mute: undefined.UndefinedOr[bool] = attr.ib(eq=False, hash=False, repr=False)
    """`builtins.True` if this member is muted in the current voice channel.

    This will be `hikari.utilities.undefined.UndefinedType if it's state is unknown.
    """

    @property
    def app(self) -> rest_app.IRESTApp:
        """Return the app that is bound to the user object."""
        return self.user.app

    @property
    def id(self) -> snowflake.Snowflake:
        return self.user.id

    @id.setter
    def id(self, value: snowflake.Snowflake) -> None:
        raise TypeError("Cannot mutate the ID of a member")

    @property
    def username(self) -> str:
        return self.user.username

    @property
    def discriminator(self) -> str:
        return self.user.discriminator

    @property
    def avatar_hash(self) -> typing.Optional[str]:
        return self.user.avatar_hash

    @property
    def is_bot(self) -> bool:
        return self.user.is_bot

    @property
    def is_system(self) -> bool:
        return self.user.is_system

    @property
    def flags(self) -> users.UserFlag:
        return self.user.flags

    @property
    def avatar(self) -> files.URL:
        return self.user.avatar

    # noinspection PyShadowingBuiltins
    def format_avatar(self, *, format: typing.Optional[str] = None, size: int = 4096) -> typing.Optional[files.URL]:
        return self.user.format_avatar(format=format, size=size)

    @property
    def default_avatar(self) -> files.URL:
        return self.user.default_avatar

    @property
    def mention(self) -> str:
        """Return a raw mention string for the given member.

        If the member has a known nickname, we always return
        a bang ("`!`") before the ID part of the mention string. This
        mimics the behaviour Discord clients tend to provide.

        Example
        -------

        ```py
        >>> some_member_without_nickname.mention
        '<@123456789123456789>'
        >>> some_member_with_nickname.mention
        '<@!123456789123456789>'
        ```

        Returns
        -------
        builtins.str
            The mention string to use.
        """
        return f"<@!{self.id}>" if isinstance(self.nickname, str) else self.user.mention

    def __str__(self) -> str:
        return str(self.user)


@attr.s(eq=True, hash=True, init=False, kw_only=True, slots=True, weakref_slot=False)
class PartialRole(snowflake.Unique):
    """Represents a partial guild bound Role object."""

    app: rest_app.IRESTApp = attr.ib(default=None, repr=False, eq=False, hash=False)
    """The client application that models may use for procedures."""

    id: snowflake.Snowflake = attr.ib(
        converter=snowflake.Snowflake, eq=True, hash=True, repr=True, factory=snowflake.Snowflake,
    )
    """The ID of this entity."""

    name: str = attr.ib(eq=False, hash=False, repr=True)
    """The role's name."""

    def __str__(self) -> str:
        return self.name


@attr.s(eq=True, hash=True, init=False, kw_only=True, slots=True, weakref_slot=False)
class Role(PartialRole):
    """Represents a guild bound Role object."""

    color: colors.Color = attr.ib(eq=False, hash=False, repr=True)
    """The colour of this role.

    This will be applied to a member's name in chat if it's their top coloured role.
    """

    guild_id: snowflake.Snowflake = attr.ib(eq=False, hash=False, repr=True)
    """The ID of the guild this role belongs to"""

    is_hoisted: bool = attr.ib(eq=False, hash=False, repr=True)
    """Whether this role is hoisting the members it's attached to in the member list.

    members will be hoisted under their highest role where this is set to `builtins.True`.
    """

    position: int = attr.ib(eq=False, hash=False, repr=True)
    """The position of this role in the role hierarchy.

    This will start at `0` for the lowest role (@everyone)
    and increase as you go up the hierarchy.
    """

    permissions: permissions_.Permission = attr.ib(eq=False, hash=False, repr=False)
    """The guild wide permissions this role gives to the members it's attached to,

    This may be overridden by channel overwrites.
    """

    is_managed: bool = attr.ib(eq=False, hash=False, repr=False)
    """Whether this role is managed by an integration."""

    is_mentionable: bool = attr.ib(eq=False, hash=False, repr=False)
    """Whether this role can be mentioned by all regardless of permissions."""

    @property
    def colour(self) -> colours.Colour:
        """Alias for the `color` field."""
        return self.color


@enum.unique
@typing.final
class IntegrationExpireBehaviour(enum.IntEnum):
    """Behavior for expiring integration subscribers."""

    REMOVE_ROLE = 0
    """Remove the role."""

    KICK = 1
    """Kick the subscriber."""


@attr.s(eq=True, hash=True, init=False, kw_only=True, slots=True, weakref_slot=False)
class IntegrationAccount:
    """An account that's linked to an integration."""

    id: str = attr.ib(eq=True, hash=True, repr=True)
    """The string ID of this (likely) third party account."""

    name: str = attr.ib(eq=False, hash=False, repr=True)
    """The name of this account."""

    def __str__(self) -> str:
        return self.name


@attr.s(eq=True, hash=True, init=False, kw_only=True, slots=True, weakref_slot=False)
class PartialIntegration(snowflake.Unique):
    """A partial representation of an integration, found in audit logs."""

    id: snowflake.Snowflake = attr.ib(
        converter=snowflake.Snowflake, eq=True, hash=True, repr=True, factory=snowflake.Snowflake,
    )
    """The ID of this entity."""

    name: str = attr.ib(eq=False, hash=False, repr=True)
    """The name of this integration."""

    type: str = attr.ib(eq=False, hash=False, repr=True)
    """The type of this integration."""

    account: IntegrationAccount = attr.ib(eq=False, hash=False, repr=False)
    """The account connected to this integration."""

    def __str__(self) -> str:
        return self.name


@attr.s(eq=True, hash=True, init=False, kw_only=True, slots=True, weakref_slot=False)
class Integration(PartialIntegration):
    """Represents a guild integration object."""

    is_enabled: bool = attr.ib(eq=False, hash=False, repr=True)
    """Whether this integration is enabled."""

    is_syncing: bool = attr.ib(eq=False, hash=False, repr=False)
    """Whether this integration is syncing subscribers/emojis."""

    role_id: typing.Optional[snowflake.Snowflake] = attr.ib(eq=False, hash=False, repr=False)
    """The ID of the managed role used for this integration's subscribers."""

    is_emojis_enabled: typing.Optional[bool] = attr.ib(eq=False, hash=False, repr=False)
    """Whether users under this integration are allowed to use it's custom emojis."""

    expire_behavior: IntegrationExpireBehaviour = attr.ib(eq=False, hash=False, repr=False)
    """How members should be treated after their connected subscription expires.

    This won't be enacted until after `GuildIntegration.expire_grace_period`
    passes.
    """

    expire_grace_period: datetime.timedelta = attr.ib(eq=False, hash=False, repr=False)
    """How many days users with expired subscriptions are given until
    `GuildIntegration.expire_behavior` is enacted out on them
    """

    user: users.UserImpl = attr.ib(eq=False, hash=False, repr=False)
    """The user this integration belongs to."""

    last_synced_at: datetime.datetime = attr.ib(eq=False, hash=False, repr=False)
    """The datetime of when this integration's subscribers were last synced."""


@attr.s(eq=True, hash=False, init=False, kw_only=True, slots=True, weakref_slot=False)
class GuildMemberBan:
    """Used to represent guild bans."""

    reason: typing.Optional[str] = attr.ib(repr=True)
    """The reason for this ban, will be `builtins.None` if no reason was given."""

    user: users.UserImpl = attr.ib(repr=True)
    """The object of the user this ban targets."""


@attr.s(eq=True, hash=True, init=False, kw_only=True, slots=True, weakref_slot=False)
@typing.final
class UnavailableGuild(snowflake.Unique):
    """An unavailable guild object, received during gateway events such as READY.

    An unavailable guild cannot be interacted with, and most information may
    be outdated if that is the case.
    """

    id: snowflake.Snowflake = attr.ib(
        converter=snowflake.Snowflake, eq=True, hash=True, repr=True, factory=snowflake.Snowflake,
    )
    """The ID of this entity."""

    # Ignore docstring not starting in an imperative mood
    @property
    def is_unavailable(self) -> bool:  # noqa: D401
        """`builtins.True` if this guild is unavailable, else `builtins.False`.

        This value is always `builtins.True`, and is only provided for consistency.
        """
        return True


@attr.s(eq=True, hash=True, init=False, kw_only=True, slots=True, weakref_slot=False)
class PartialGuild(snowflake.Unique):
    """Base object for any partial guild objects."""

    app: rest_app.IRESTApp = attr.ib(default=None, repr=False, eq=False, hash=False)
    """The client application that models may use for procedures."""

    id: snowflake.Snowflake = attr.ib(
        converter=snowflake.Snowflake, eq=True, hash=True, repr=True, factory=snowflake.Snowflake,
    )
    """The ID of this entity."""

    name: str = attr.ib(eq=False, hash=False, repr=True)
    """The name of the guild."""

    icon_hash: typing.Optional[str] = attr.ib(eq=False, hash=False, repr=False)
    """The hash for the guild icon, if there is one."""

    features: typing.Sequence[GuildFeatureish] = attr.ib(eq=False, hash=False, repr=False)
    """A list of the features in this guild."""

    def __str__(self) -> str:
        return self.name

    @property
    def shard_id(self) -> typing.Optional[int]:
        """Return the ID of the shard this guild is served by.

        This may return `None` if the application does not have a gateway
        connection.
        """
        try:
            # This is only sensible if there is a shard.
            return (self.id >> 22) % typing.cast(int, getattr(self.app, "shard_count"))
        except (TypeError, AttributeError, NameError):
            return None

    @property
    def icon_url(self) -> typing.Optional[files.URL]:
        """Icon for the guild, if set; otherwise `builtins.None`."""
        return self.format_icon()

    def format_icon(self, *, format_: typing.Optional[str] = None, size: int = 4096) -> typing.Optional[files.URL]:
        """Generate the guild's icon, if set.

        Parameters
        ----------
        format_ : builtins.str or builtins.None
            The format to use for this URL, defaults to `png` or `gif`.
            Supports `png`, `jpeg`, `jpg`, `webp` and `gif` (when
            animated).

            If `builtins.None`, then the correct default format is determined
            based on whether the icon is animated or not.
        size : builtins.int
            The size to set for the URL, defaults to `4096`.
            Can be any power of two between 16 and 4096.

        Returns
        -------
        hikari.utilities.files.URL or builtins.None
            The URL to the resource, or `builtins.None` if no icon is set.

        Raises
        ------
        builtins.ValueError
            If `size` is not a power of two or not between 16 and 4096.
        """
        if self.icon_hash is None:
            return None

        if format_ is None:
            if self.icon_hash.startswith("a_"):
                format_ = "gif"
            else:
                format_ = "png"

        return routes.CDN_GUILD_ICON.compile_to_file(
            constants.CDN_URL, guild_id=self.id, hash=self.icon_hash, size=size, file_format=format_,
        )


@attr.s(eq=True, hash=True, init=False, kw_only=True, slots=True, weakref_slot=False)
class GuildPreview(PartialGuild):
    """A preview of a guild with the `GuildFeature.PUBLIC` feature."""

    splash_hash: typing.Optional[str] = attr.ib(eq=False, hash=False, repr=False)
    """The hash of the splash for the guild, if there is one."""

    discovery_splash_hash: typing.Optional[str] = attr.ib(eq=False, hash=False, repr=False)
    """The hash of the discovery splash for the guild, if there is one."""

    emojis: typing.Mapping[snowflake.Snowflake, emojis_.KnownCustomEmoji] = attr.ib(eq=False, hash=False, repr=False)
    """The mapping of IDs to the emojis this guild provides."""

    approximate_presence_count: int = attr.ib(eq=False, hash=False, repr=True)
    """The approximate amount of presences in guild."""

    approximate_member_count: int = attr.ib(eq=False, hash=False, repr=True)
    """The approximate amount of members in this guild."""

    description: typing.Optional[str] = attr.ib(eq=False, hash=False, repr=False)
    """The guild's description, if set."""

    @property
    def splash_url(self) -> typing.Optional[files.URL]:
        """Splash for the guild, if set."""
        return self.format_splash()

    def format_splash(self, *, format_: str = "png", size: int = 4096) -> typing.Optional[files.URL]:
        """Generate the guild's splash image, if set.

        Parameters
        ----------
        format_ : builtins.str
            The format to use for this URL, defaults to `png`.
            Supports `png`, `jpeg`, `jpg` and `webp`.
        size : builtins.int
            The size to set for the URL, defaults to `4096`.
            Can be any power of two between 16 and 4096.

        Returns
        -------
        hikari.utilities.files.URL or builtins.None
            The URL to the splash, or `builtins.None` if not set.

        Raises
        ------
        builtins.ValueError
            If `size` is not a power of two or not between 16 and 4096.
        """
        if self.splash_hash is None:
            return None

        return routes.CDN_GUILD_SPLASH.compile_to_file(
            constants.CDN_URL, guild_id=self.id, hash=self.splash_hash, size=size, file_format=format_,
        )

    @property
    def discovery_splash(self) -> typing.Optional[files.URL]:
        """Discovery splash for the guild, if set."""
        return self.format_discovery_splash()

    def format_discovery_splash(self, *, format_: str = "png", size: int = 4096) -> typing.Optional[files.URL]:
        """Generate the guild's discovery splash image, if set.

        Parameters
        ----------
        format_ : builtins.str
            The format to use for this URL, defaults to `png`.
            Supports `png`, `jpeg`, `jpg` and `webp`.
        size : builtins.int
            The size to set for the URL, defaults to `4096`.
            Can be any power of two between 16 and 4096.

        Returns
        -------
        hikari.utilities.files.URL or builtins.None
            The string URL.

        Raises
        ------
        builtins.ValueError
            If `size` is not a power of two or not between 16 and 4096.
        """
        if self.discovery_splash_hash is None:
            return None

        return routes.CDN_GUILD_DISCOVERY_SPLASH.compile_to_file(
            constants.CDN_URL, guild_id=self.id, hash=self.discovery_splash_hash, size=size, file_format=format_,
        )


@attr.s(eq=True, hash=True, init=False, kw_only=True, slots=True, weakref_slot=False)
class Guild(PartialGuild):
    """A representation of a guild on Discord."""

    splash_hash: typing.Optional[str] = attr.ib(eq=False, hash=False, repr=False)
    """The hash of the splash for the guild, if there is one."""

    discovery_splash_hash: typing.Optional[str] = attr.ib(eq=False, hash=False, repr=False)
    """The hash of the discovery splash for the guild, if there is one."""

    owner_id: snowflake.Snowflake = attr.ib(eq=False, hash=False, repr=True)
    """The ID of the owner of this guild."""

    region: str = attr.ib(eq=False, hash=False, repr=False)
    """The voice region for the guild."""

    afk_channel_id: typing.Optional[snowflake.Snowflake] = attr.ib(eq=False, hash=False, repr=False)
    """The ID for the channel that AFK voice users get sent to.

    If `builtins.None`, then no AFK channel is set up for this guild.
    """

    afk_timeout: datetime.timedelta = attr.ib(eq=False, hash=False, repr=False)
    """Timeout for activity before a member is classed as AFK.

    How long a voice user has to be AFK for before they are classed as being
    AFK and are moved to the AFK channel (`Guild.afk_channel_id`).
    """

    embed_channel_id: typing.Optional[snowflake.Snowflake] = attr.ib(eq=False, hash=False, repr=False)
    """The channel ID that the guild embed will generate an invite to.

    Will be `builtins.None` if invites are disabled for this guild's embed.

    !!! deprecated
        Use `widget_channel_id` instead.
    """

    verification_level: GuildVerificationLevel = attr.ib(eq=False, hash=False, repr=False)
    """The verification level required for a user to participate in this guild."""

    default_message_notifications: GuildMessageNotificationsLevel = attr.ib(eq=False, hash=False, repr=False)
    """The default setting for message notifications in this guild."""

    explicit_content_filter: GuildExplicitContentFilterLevel = attr.ib(eq=False, hash=False, repr=False)
    """The setting for the explicit content filter in this guild."""

    mfa_level: GuildMFALevel = attr.ib(eq=False, hash=False, repr=False)
    """The required MFA level for users wishing to participate in this guild."""

    application_id: typing.Optional[snowflake.Snowflake] = attr.ib(eq=False, hash=False, repr=False)
    """The ID of the application that created this guild.

    This will always be `builtins.None` for guilds that weren't created by a bot.
    """

    is_widget_enabled: typing.Optional[bool] = attr.ib(eq=False, hash=False, repr=False)
    """Describes whether the guild widget is enabled or not.

    If this information is not present, this will be `builtins.None`.
    """

    widget_channel_id: typing.Optional[snowflake.Snowflake] = attr.ib(eq=False, hash=False, repr=False)
    """The channel ID that the widget's generated invite will send the user to.

    If this information is unavailable or this isn't enabled for the guild then
    this will be `builtins.None`.
    """

    system_channel_id: typing.Optional[snowflake.Snowflake] = attr.ib(eq=False, hash=False, repr=False)
    """The ID of the system channel or `builtins.None` if it is not enabled.

    Welcome messages and Nitro boost messages may be sent to this channel.
    """

    system_channel_flags: GuildSystemChannelFlag = attr.ib(eq=False, hash=False, repr=False)
    """Flags for the guild system channel to describe which notifications are suppressed."""

    rules_channel_id: typing.Optional[snowflake.Snowflake] = attr.ib(eq=False, hash=False, repr=False)
    """The ID of the channel where guilds with the `GuildFeature.PUBLIC`
    `features` display rules and guidelines.

    If the `GuildFeature.PUBLIC` feature is not defined, then this is `builtins.None`.
    """

    max_presences: typing.Optional[int] = attr.ib(eq=False, hash=False, repr=False)
    """The maximum number of presences for the guild.

    If this is `builtins.None`, then the default value is used (currently 25000).
    """

    max_members: typing.Optional[int] = attr.ib(eq=False, hash=False, repr=False)
    """The maximum number of members allowed in this guild.

    This information may not be present, in which case, it will be `builtins.None`.
    """

    max_video_channel_users: typing.Optional[int] = attr.ib(eq=False, hash=False, repr=False)
    """The maximum number of users allowed in a video channel together.

    This information may not be present, in which case, it will be `builtins.None`.
    """

    vanity_url_code: typing.Optional[str] = attr.ib(eq=False, hash=False, repr=False)
    """The vanity URL code for the guild's vanity URL.

    This is only present if `GuildFeature.VANITY_URL` is in `Guild.features` for
    this guild. If not, this will always be `builtins.None`.
    """

    description: typing.Optional[str] = attr.ib(eq=False, hash=False, repr=False)
    """The guild's description.

    This is only present if certain `GuildFeature`'s are set in
    `Guild.features` for this guild. Otherwise, this will always be `builtins.None`.
    """

    banner_hash: typing.Optional[str] = attr.ib(eq=False, hash=False, repr=False)
    """The hash for the guild's banner.

    This is only present if the guild has `GuildFeature.BANNER` in
    `Guild.features` for this guild. For all other purposes, it is `builtins.None`.
    """

    premium_tier: GuildPremiumTier = attr.ib(eq=False, hash=False, repr=False)
    """The premium tier for this guild."""

    premium_subscription_count: typing.Optional[int] = attr.ib(eq=False, hash=False, repr=False)
    """The number of nitro boosts that the server currently has.

    This information may not be present, in which case, it will be `builtins.None`.
    """

    preferred_locale: str = attr.ib(eq=False, hash=False, repr=False)
    """The preferred locale to use for this guild.

    This can only be change if `GuildFeature.PUBLIC` is in `Guild.features`
    for this guild and will otherwise default to `en-US`.
    """

    public_updates_channel_id: typing.Optional[snowflake.Snowflake] = attr.ib(eq=False, hash=False, repr=False)
    """The channel ID of the channel where admins and moderators receive notices
    from Discord.

    This is only present if `GuildFeature.PUBLIC` is in `Guild.features` for
    this guild. For all other purposes, it should be considered to be `builtins.None`.
    """

    @abc.abstractmethod
    def cached_roles(self) -> iterators.LazyIterator[Role]:
        """Generate a lazy iterator across all roles."""

    @abc.abstractmethod
    def cached_emojis(self) -> iterators.LazyIterator[emojis_.KnownCustomEmoji]:
        """Generate a lazy iterator across all emojis."""

    @abc.abstractmethod
    async def get_cached_role(self, role: typing.Union[Role, snowflake.UniqueObject]) -> typing.Optional[Role]:
        """Get a role from the cache by an ID."""

    @abc.abstractmethod
    async def get_cached_emoji(
        self, emoji: typing.Union[emojis_.CustomEmoji, snowflake.UniqueObject]
    ) -> typing.Optional[emojis_.KnownCustomEmoji]:
        """Get an emoji from the cache by an ID."""

    @property
    def splash_url(self) -> typing.Optional[files.URL]:
        """Splash for the guild, if set."""
        return self.format_splash()

    def format_splash(self, *, format_: str = "png", size: int = 4096) -> typing.Optional[files.URL]:
        """Generate the guild's splash image, if set.

        Parameters
        ----------
        format_ : builtins.str
            The format to use for this URL, defaults to `png`.
            Supports `png`, `jpeg`, `jpg` and `webp`.
        size : builtins.int
            The size to set for the URL, defaults to `4096`.
            Can be any power of two between 16 and 4096.

        Returns
        -------
        hikari.utilities.files.URL or builtins.None
            The URL to the splash, or `builtins.None` if not set.

        Raises
        ------
        builtins.ValueError
            If `size` is not a power of two or not between 16 and 4096.
        """
        if self.splash_hash is None:
            return None

        return routes.CDN_GUILD_SPLASH.compile_to_file(
            constants.CDN_URL, guild_id=self.id, hash=self.splash_hash, size=size, file_format=format_,
        )

    @property
    def discovery_splash(self) -> typing.Optional[files.URL]:
        """Discovery splash for the guild, if set."""
        return self.format_discovery_splash()

    def format_discovery_splash(self, *, format_: str = "png", size: int = 4096) -> typing.Optional[files.URL]:
        """Generate the guild's discovery splash image, if set.

        Parameters
        ----------
        format_ : builtins.str
            The format to use for this URL, defaults to `png`.
            Supports `png`, `jpeg`, `jpg` and `webp`.
        size : builtins.int
            The size to set for the URL, defaults to `4096`.
            Can be any power of two between 16 and 4096.

        Returns
        -------
        hikari.utilities.files.URL or builtins.None
            The string URL.

        Raises
        ------
        builtins.ValueError
            If `size` is not a power of two or not between 16 and 4096.
        """
        if self.discovery_splash_hash is None:
            return None

        return routes.CDN_GUILD_DISCOVERY_SPLASH.compile_to_file(
            constants.CDN_URL, guild_id=self.id, hash=self.discovery_splash_hash, size=size, file_format=format_,
        )

    @property
    def banner(self) -> typing.Optional[files.URL]:
        """Banner for the guild, if set."""
        return self.format_banner()

    def format_banner(self, *, format_: str = "png", size: int = 4096) -> typing.Optional[files.URL]:
        """Generate the guild's banner image, if set.

        Parameters
        ----------
        format_ : builtins.str
            The format to use for this URL, defaults to `png`.
            Supports `png`, `jpeg`, `jpg` and `webp`.
        size : builtins.int
            The size to set for the URL, defaults to `4096`.
            Can be any power of two between 16 and 4096.

        Returns
        -------
        hikari.utilities.files.URL or builtins.None
            The URL of the banner, or `builtins.None` if no banner is set.

        Raises
        ------
        builtins.ValueError
            If `size` is not a power of two or not between 16 and 4096.
        """
        if self.banner_hash is None:
            return None

        return routes.CDN_GUILD_BANNER.compile_to_file(
            constants.CDN_URL, guild_id=self.id, hash=self.banner_hash, size=size, file_format=format_,
        )


class RESTGuild(Guild):
    """Guild specialization that is sent via the REST API only."""

    _roles: typing.Mapping[snowflake.Snowflake, Role] = attr.ib(eq=False, hash=False, repr=False)
    """The roles in this guild, represented as a mapping of ID to role object."""

    _emojis: typing.Mapping[snowflake.Snowflake, emojis_.KnownCustomEmoji] = attr.ib(eq=False, hash=False, repr=False)
    """A mapping of IDs to the objects of the emojis this guild provides."""

    is_embed_enabled: typing.Optional[bool] = attr.ib(eq=False, hash=False, repr=False)
    """Defines if the guild embed is enabled or not.

    This information may not be present, in which case, it will be `builtins.None`
    instead. This will be `builtins.None` for guilds that the bot is not a member in.

    !!! deprecated
        Use `is_widget_enabled` instead.
    """

    approximate_member_count: typing.Optional[int] = attr.ib(eq=False, hash=False, repr=False)
    """The approximate number of members in the guild.

    This information will be provided by HTTP API calls fetching the guilds that
    a bot account is in. For all other purposes, this should be expected to
    remain `builtins.None`.
    """

    approximate_active_member_count: typing.Optional[int] = attr.ib(eq=False, hash=False, repr=False)
    """The approximate number of members in the guild that are not offline.

    This information will be provided by HTTP API calls fetching the guilds that
    a bot account is in. For all other purposes, this should be expected to
    remain `builtins.None`.
    """

    def cached_roles(self) -> iterators.FlatLazyIterator[Role]:
        return iterators.FlatLazyIterator(self._roles.values())

    def cached_emojis(self) -> iterators.FlatLazyIterator[emojis_.KnownCustomEmoji]:
        return iterators.FlatLazyIterator(self._emojis.values())

    async def get_cached_role(self, role: typing.Union[Role, snowflake.UniqueObject]) -> typing.Optional[Role]:
        return self._roles.get(snowflake.Snowflake(int(role)))

    async def get_cached_emoji(
        self, emoji: typing.Union[emojis_.CustomEmoji, snowflake.UniqueObject]
    ) -> typing.Optional[emojis_.KnownCustomEmoji]:
        return self._emojis.get(snowflake.Snowflake(int(emoji)))


@attr.s(eq=True, hash=True, init=False, kw_only=True, slots=True)
class GatewayGuild(Guild):
    """Guild specialization that is sent via the gateway only."""

    my_permissions: typing.Optional[permissions_.Permission] = attr.ib(eq=False, hash=False, repr=False)
    """The guild-level permissions that apply to the bot user.

    This will not take into account permission overwrites or implied
    permissions (for example, `ADMINISTRATOR` implies all other permissions).
    """

    joined_at: typing.Optional[datetime.datetime] = attr.ib(eq=False, hash=False, repr=False)
    """The date and time that the bot user joined this guild.

    This information is only available if the guild was sent via a `GUILD_CREATE`
    event. If the guild is received from any other place, this will always be
    `builtins.None`.
    """

    is_large: typing.Optional[bool] = attr.ib(eq=False, hash=False, repr=False)
    """Whether the guild is considered to be large or not.

    This information is only available if the guild was sent via a `GUILD_CREATE`
    event. If the guild is received from any other place, this will always be
    `builtins.None`.

    The implications of a large guild are that presence information will not be
    sent about members who are offline or invisible.
    """

    member_count: typing.Optional[int] = attr.ib(eq=False, hash=False, repr=False)
    """The number of members in this guild.

    This information is only available if the guild was sent via a `GUILD_CREATE`
    event. If the guild is received from any other place, this will always be
    `builtins.None`.
    """

    def cached_roles(self) -> iterators.LazyIterator[Role]:
        return self.app.cache.get_roles_for_guild(self.id)

    def cached_emojis(self) -> iterators.LazyIterator[emojis_.KnownCustomEmoji]:
        return self.app.cache.get_emojis_for_guild(self.id)

    def cached_members(self) -> iterators.LazyIterator[Member]:
        return self.app.cache.get_members_for_guild(self.id)

    def cached_channels(self) -> iterators.LazyIterator[channels_.GuildChannel]:
        return self.app.cache.get_channels_for_guild(self.id)

    def cached_presences(self) -> iterators.LazyIterator[presences_.MemberPresence]:
        return self.app.cache.get_presences_for_guild(self.id)

    async def get_cached_role(self, role: typing.Union[Role, snowflake.UniqueObject]) -> typing.Optional[Role]:
        return await self.app.cache.get_role_for_guild(self.id, snowflake.Snowflake(int(role)))

    async def get_cached_emoji(
        self, emoji: typing.Union[emojis_.CustomEmoji, snowflake.UniqueObject]
    ) -> typing.Optional[emojis_.KnownCustomEmoji]:
        return await self.app.cache.get_emoji_for_guild(self.id, snowflake.Snowflake(int(emoji)))

    async def get_cached_channel(
        self, channel: typing.Union[channels_.GuildChannel, snowflake.UniqueObject],
    ) -> typing.Optional[channels_.GuildChannel]:
        return await self.app.cache.get_channel_for_guild(self.id, snowflake.Snowflake(int(channel)))

    async def get_cached_member(
        self, user: typing.Union[users.User, snowflake.UniqueObject]
    ) -> typing.Optional[Member]:
        return await self.app.cache.get_member_for_guild(self.id, snowflake.Snowflake(int(user)))

    async def get_cached_presence(
        self, user: typing.Union[users.User, snowflake.UniqueObject]
    ) -> typing.Optional[presences_.MemberPresence]:
        return await self.app.cache.get_presence_for_guild(self.id, snowflake.Snowflake(int(user)))
