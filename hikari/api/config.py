# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021-present davfsa
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
"""Core interface for Hikari's configuration dataclasses."""
from __future__ import annotations

__all__: typing.Sequence[str] = ("CacheComponents", "CacheSettings", "HTTPSettings", "ProxySettings")

import abc
import typing

from hikari.internal import enums

if typing.TYPE_CHECKING:
    import ssl as ssl_


class CacheComponents(enums.Flag):
    """Flags to control the cache components."""

    NONE = 0
    """Disables the cache."""

    GUILDS = 1 << 0
    """Enables the guild cache."""

    GUILD_CHANNELS = 1 << 1
    """Enables the guild channels cache."""

    MEMBERS = 1 << 2
    """Enables the members cache."""

    ROLES = 1 << 3
    """Enables the roles cache."""

    INVITES = 1 << 4
    """Enables the invites cache."""

    EMOJIS = 1 << 5
    """Enables the emojis cache."""

    PRESENCES = 1 << 6
    """Enables the presences cache."""

    VOICE_STATES = 1 << 7
    """Enables the voice states cache."""

    MESSAGES = 1 << 8
    """Enables the messages cache."""

    ME = 1 << 9
    """Enables the me cache."""

    DM_CHANNEL_IDS = 1 << 10
    """Enables the DM channel IDs cache."""

    GUILD_STICKERS = 1 << 11
    """Enables the guild stickers cache."""

    GUILD_THREADS = 1 << 12
    """Enables the guild threads cache."""

    MY_MEMBER = 1 << 13
    """Enables the members cache for the bot."""

    ALL = (
        GUILDS
        | GUILD_CHANNELS
        | MEMBERS
        | ROLES
        | INVITES
        | EMOJIS
        | PRESENCES
        | VOICE_STATES
        | MESSAGES
        | ME
        | DM_CHANNEL_IDS
        | GUILD_STICKERS
        | GUILD_THREADS
        | MY_MEMBER
    )
    """Fully enables the cache."""


class ProxySettings(abc.ABC):
    """Settings for configuring an HTTP-based proxy."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def url(self) -> typing.Union[None, str]:
        """Proxy URL to use.

        If this is `None` then no explicit proxy is being used.
        """

    @property
    @abc.abstractmethod
    def trust_env(self) -> bool:
        """Toggle whether to look for a `netrc` file or environment variables.

        If `True`, and no `url` is given on this object, then
        `HTTP_PROXY` and `HTTPS_PROXY` will be used from the environment
        variables, or a `netrc` file may be read to determine credentials.

        If `False`, then this information is instead ignored.

        .. note::
            For more details of using `netrc`, visit:
            https://www.gnu.org/software/inetutils/manual/html_node/The-_002enetrc-file.html
        """


class HTTPSettings(abc.ABC):
    """Settings to control HTTP clients."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def max_redirects(self) -> typing.Optional[int]:
        """Behavior for handling redirect HTTP responses.

        If a `int`, allow following redirects from `3xx` HTTP responses
        for up to this many redirects. Exceeding this value will raise an
        exception.

        If `None`, then disallow any redirects.

        The default is to disallow this behavior for security reasons.

        Generally, it is safer to keep this disabled. You may find a case in the
        future where you need to enable this if Discord change their URL without
        warning.

        .. note::
            This will only apply to the REST API. WebSockets remain unaffected
            by any value set here.
        """

    @property
    @abc.abstractmethod
    def ssl(self) -> ssl_.SSLContext:
        """SSL context to use.

        This may be assigned a `bool` or an `ssl.SSLContext` object.

        If assigned to `True`, a default SSL context is generated by
        this class that will enforce SSL verification. This is then stored in
        this field.

        If `False`, then a default SSL context is generated by this
        class that will **NOT** enforce SSL verification. This is then stored
        in this field.

        If an instance of `ssl.SSLContext`, then this context will be used.

        .. warning::
            Setting a custom value here may have security implications, or
            may result in the application being unable to connect to Discord
            at all.

        .. warning::
            Disabling SSL verification is almost always unadvised. This
            is because your application will no longer check whether you are
            connecting to Discord, or to some third party spoof designed
            to steal personal credentials such as your application token.

            There may be cases where SSL certificates do not get updated,
            and in this case, you may find that disabling this explicitly
            allows you to work around any issues that are occurring, but
            you should immediately seek a better solution where possible
            if any form of personal security is in your interest.
        """


class CacheSettings(abc.ABC):
    """Settings to control the cache."""

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractmethod
    def components(self) -> CacheComponents:
        """Cache components to use."""

    @property
    @abc.abstractmethod
    def only_cache_my_member(self) -> bool:
        """This reduces the members cache to only the bot itself.
        
        This will have no effect if the members cache is not enabled.
        
        Defaults to `False`.
        """
