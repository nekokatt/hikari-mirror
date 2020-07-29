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
"""Event handling logic for more info."""

from __future__ import annotations

__all__: typing.Final[typing.List[str]] = ["StatefulEventManagerImpl"]

import typing

from hikari.events import other as other_events
from hikari.impl import event_manager_base
from hikari.models import channels
from hikari.models import guilds

# from hikari.models import presences

if typing.TYPE_CHECKING:
    from hikari.api import shard as gateway_shard
    from hikari.events import guild as guild_events
    from hikari.utilities import data_binding


class StatefulEventManagerImpl(event_manager_base.EventManagerComponentBase):
    """Provides event handling logic for Discord events."""

    __slots__: typing.Sequence[str] = ()

    async def on_connected(self, shard: gateway_shard.IGatewayShard, _: data_binding.JSONObject) -> None:
        """Handle connection events.

        This is a synthetic event produced by the gateway implementation in
        Hikari.
        """
        # TODO: this should be in entity factory
        await self.dispatch(other_events.ConnectedEvent(shard=shard))

    async def on_disconnected(self, shard: gateway_shard.IGatewayShard, _: data_binding.JSONObject) -> None:
        """Handle disconnection events.

        This is a synthetic event produced by the gateway implementation in
        Hikari.
        """
        # TODO: this should be in entity factory
        await self.dispatch(other_events.DisconnectedEvent(shard=shard))

    async def on_ready(self, shard: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#ready for more info."""
        # TODO: cache unavailable guilds on startup, I didn't bother for the time being.
        event = self.app.entity_factory.deserialize_ready_event(shard, payload)
        self.app.cache.update_me(event.my_user)
        self.app.cache.set_initial_unavailable_guilds(event.unavailable_guilds.keys())
        await self.dispatch(event)

    async def on_resumed(self, shard: gateway_shard.IGatewayShard, _: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#resumed for more info."""
        # TODO: this should be in entity factory
        await self.dispatch(other_events.ResumedEvent(shard=shard))

    async def on_channel_create(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#channel-create for more info."""
        event = self.app.entity_factory.deserialize_channel_create_event(payload)

        if isinstance(event.channel, channels.GuildChannel):
            self.app.cache.set_guild_channel(event.channel)
        else:
            self.app.cache.set_dm_channel(typing.cast(channels.DMChannel, event.channel))

        await self.dispatch(event)

    async def on_channel_update(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#channel-update for more info."""
        event = self.app.entity_factory.deserialize_channel_update_event(payload)

        if isinstance(event.channel, channels.GuildChannel):
            self.app.cache.update_guild_channel(event.channel)
        else:
            self.app.cache.update_dm_channel(typing.cast(channels.DMChannel, event.channel))

        await self.dispatch(event)

    async def on_channel_delete(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#channel-delete for more info."""
        event = self.app.entity_factory.deserialize_channel_delete_event(payload)

        if isinstance(event.channel, channels.GuildChannel):
            self.app.cache.delete_guild_channel(event.channel.id)
        else:
            self.app.cache.delete_dm_channel(typing.cast(channels.DMChannel, event.channel).recipient.id)

        await self.dispatch(event)

    async def on_channel_pins_update(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#channel-pins-update for more info."""
        # TODO: we need a method for this specifically
        await self.dispatch(self.app.entity_factory.deserialize_channel_pins_update_event(payload))

    async def on_guild_create(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#guild-create for more info."""
        event = self.app.entity_factory.deserialize_guild_create_event(payload)
        self.app.cache.update_guild(event.guild)

        # self.app.cache.clear_guild_channels(event.guild.id)
        # for channel in event.channels.values():
        #     self.app.cache.set_guild_channel(channel)
        #
        self.app.cache.clear_emojis_for_guild(event.guild.id)
        for emoji in event.emojis.values():
            self.app.cache.set_emoji(emoji)

        self.app.cache.clear_roles_for_guild(event.guild.id)
        for role in event.roles.values():
            self.app.cache.set_role(role)

        self.app.cache.clear_members_for_guild(
            event.guild.id
        )  # TODO: do we really want to invalidate these all after an outage.
        for member in event.members.values():
            self.app.cache.set_member(member)

        # self.app.cache.clear_presences(event.guild.id)
        # for presence in event.presences.values():
        #     self.app.cache.set_presence(presence)

        for voice_state in event.voice_states.values():
            self.app.cache.set_voice_state(voice_state)

        await self.dispatch(event)

    async def on_guild_update(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#guild-update for more info."""
        event = self.app.entity_factory.deserialize_guild_update_event(payload)
        self.app.cache.update_guild(event.guild)

        self.app.cache.clear_roles_for_guild(event.guild.id)
        for role in event.roles.values():  # TODO: do we actually get this here?
            self.app.cache.set_role(role)

        self.app.cache.clear_emojis_for_guild(event.guild.id)  # TODO: do we actually get this here?
        for emoji in event.emojis.values():
            self.app.cache.set_emoji(emoji)

        await self.dispatch(event)

    async def on_guild_delete(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#guild-delete for more info."""
        event: typing.Union[guild_events.GuildUnavailableEvent, guild_events.GuildLeaveEvent]
        if payload.get("unavailable", False):
            event = self.app.entity_factory.deserialize_guild_unavailable_event(payload)
            guild = guilds.UnavailableGuild()
            guild.id = event.id
            self.app.cache.set_guild_availability(guild.id, False)

        else:
            event = self.app.entity_factory.deserialize_guild_leave_event(payload)
            self.app.cache.delete_guild(event.id)
            # TODO Remove other entities here?

        await self.dispatch(event)

    async def on_guild_ban_add(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#guild-ban-add for more info."""
        await self.dispatch(self.app.entity_factory.deserialize_guild_ban_add_event(payload))

    async def on_guild_ban_remove(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#guild-ban-remove for more info."""
        await self.dispatch(self.app.entity_factory.deserialize_guild_ban_remove_event(payload))

    async def on_guild_emojis_update(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#guild-emojis-update for more info."""
        event = self.app.entity_factory.deserialize_guild_emojis_update_event(payload)
        self.app.cache.clear_emojis_for_guild(event.guild_id)

        for emoji in event.emojis.values():
            self.app.cache.set_emoji(emoji)

        await self.dispatch(event)

    async def on_guild_integrations_update(
        self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject
    ) -> None:
        """See https://discord.com/developers/docs/topics/gateway#guild-integrations-update for more info."""
        await self.dispatch(self.app.entity_factory.deserialize_guild_integrations_update_event(payload))

    async def on_guild_member_add(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#guild-member-add for more info."""
        event = self.app.entity_factory.deserialize_guild_member_add_event(payload)
        self.app.cache.update_member(event.member)
        await self.dispatch(event)

    async def on_guild_member_remove(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#guild-member-remove for more info."""
        event = self.app.entity_factory.deserialize_guild_member_remove_event(payload)
        self.app.cache.update_user(event.user)
        self.app.cache.delete_member(event.guild_id, event.user.id)
        await self.dispatch(event)

    async def on_guild_member_update(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#guild-member-update for more info."""
        event = self.app.entity_factory.deserialize_guild_member_update_event(payload)
        self.app.cache.update_member(event.member)
        await self.dispatch(event)

    async def on_guild_members_chunk(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#guild-members-chunk for more info."""
        # TODO: implement chunking components.
        event = self.app.entity_factory.deserialize_guild_member_chunk_event(payload)

        for member in event.members.values():
            self.app.cache.set_member(member)

        for presence in event.presences.values():
            self.app.cache.set_presence(presence)

        await self.dispatch(event)

    async def on_guild_role_create(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#guild-role-create for more info."""
        event = self.app.entity_factory.deserialize_guild_role_create_event(payload)
        self.app.cache.set_role(event.role)
        await self.dispatch(event)

    async def on_guild_role_update(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#guild-role-update for more info."""
        event = self.app.entity_factory.deserialize_guild_role_update_event(payload)
        self.app.cache.update_role(event.role)
        await self.dispatch(event)

    async def on_guild_role_delete(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#guild-role-delete for more info."""
        event = self.app.entity_factory.deserialize_guild_role_delete_event(payload)
        self.app.cache.delete_role(event.role_id)
        await self.dispatch(event)

    async def on_invite_create(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#invite-create for more info."""
        event = self.app.entity_factory.deserialize_invite_create_event(payload)
        self.app.cache.set_invite(event.invite)
        await self.dispatch(event)

    async def on_invite_delete(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#invite-delete for more info."""
        event = self.app.entity_factory.deserialize_invite_delete_event(payload)
        self.app.cache.delete_invite(event.code)
        await self.dispatch(event)

    async def on_message_create(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#message-create for more info."""
        await self.dispatch(self.app.entity_factory.deserialize_message_create_event(payload))

    # TODO: message cache.

    async def on_message_update(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#message-update for more info."""
        await self.dispatch(self.app.entity_factory.deserialize_message_update_event(payload))

    async def on_message_delete(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#message-delete for more info."""
        await self.dispatch(self.app.entity_factory.deserialize_message_delete_event(payload))

    async def on_message_delete_bulk(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#message-delete-bulk for more info."""
        await self.dispatch(self.app.entity_factory.deserialize_message_delete_bulk_event(payload))

    async def on_message_reaction_add(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#message-reaction-add for more info."""
        await self.dispatch(self.app.entity_factory.deserialize_message_reaction_add_event(payload))

    # TODO: this is unlikely but reaction cache?

    async def on_message_reaction_remove(
        self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject
    ) -> None:
        """See https://discord.com/developers/docs/topics/gateway#message-reaction-remove for more info."""
        await self.dispatch(self.app.entity_factory.deserialize_message_reaction_remove_event(payload))

    async def on_message_reaction_remove_all(
        self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject
    ) -> None:
        """See https://discord.com/developers/docs/topics/gateway#message-reaction-remove-all for more info."""
        await self.dispatch(self.app.entity_factory.deserialize_message_reaction_remove_all_event(payload))

    async def on_message_reaction_remove_emoji(
        self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject
    ) -> None:
        """See https://discord.com/developers/docs/topics/gateway#message-reaction-remove-emoji for more info."""
        await self.dispatch(self.app.entity_factory.deserialize_message_reaction_remove_emoji_event(payload))

    async def on_presence_update(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#presence-update for more info."""
        event = self.app.entity_factory.deserialize_presence_update_event(payload)

        # if event.presence.visible_status is presences.Status.OFFLINE:
        #     self.app.cache.delete_presence(event.presence.guild_id, event.presence.user_id)
        # else:
        #     self.app.cache.update_presence(event.presence)
        #
        # if event.partial_user is not None:
        #     self.app.cache.update_user(event.partial_user)

        await self.dispatch(event)

    async def on_typing_start(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#typing-start for more info."""
        await self.dispatch(self.app.entity_factory.deserialize_typing_start_event(payload))

    async def on_user_update(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#user-update for more info."""
        event = self.app.entity_factory.deserialize_own_user_update_event(payload)
        self.app.cache.update_me(event.my_user)
        await self.dispatch(event)

    async def on_voice_state_update(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#voice-state-update for more info."""
        event = self.app.entity_factory.deserialize_voice_state_update_event(payload)

        if event.state.channel_id is None:
            self.app.cache.delete_voice_state(event.state.guild_id, event.state.user_id)
        else:
            self.app.cache.update_voice_state(event.state)

        await self.dispatch(event)

    async def on_voice_server_update(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#voice-server-update for more info."""
        await self.dispatch(self.app.entity_factory.deserialize_voice_server_update_event(payload))

    async def on_webhooks_update(self, _: gateway_shard.IGatewayShard, payload: data_binding.JSONObject) -> None:
        """See https://discord.com/developers/docs/topics/gateway#webhooks-update for more info."""
        await self.dispatch(self.app.entity_factory.deserialize_webhook_update_event(payload))
