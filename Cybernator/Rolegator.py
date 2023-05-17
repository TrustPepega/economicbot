import traceback
import disnake
import asyncio
from disnake.ext import commands
from disnake import utils


class Rolegator:
    def __init__(self, bot, **kwargs):
        self.bot = bot
        self.emoji_role = kwargs.get('emoji_role', dict)
        self.guild_id = kwargs.get('guild_id', int)
        self.guild_roles = kwargs.get('guild_roles', list)
        self.channel_id = kwargs.get('channel_id', int)
        self.message_id = kwargs.get('message_id', int)
        self.role_remove = kwargs.get('role_remove', False)
        self.role_member_join = kwargs.get('role_member_join', True)
#        self.max_role = kwargs.get('max_role', int)
#        self.white_roles = kwargs.get('green_roles', list)

    async def on_member_join(self, member):
        if self.role_member_join:
            if member.guild.id == self.guild_id:
                for i in self.guild_roles:
                    role = utils.get(member.guild.roles, id=i)
                    await member.add_roles(role)
        else:
            pass

    async def on_ready(self):
        message = await self.bot.get_channel(self.channel_id).fetch_message(self.message_id)
        for i in self.emoji_role:
            await message.add_reaction(i)

    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return False
        message = await self.bot.get_channel(self.channel_id).fetch_message(self.message_id)
        # member = message.guild.get_member(payload.user_id)
        member = await message.guild.fetch_member(payload.user_id)
        if payload.message_id == self.message_id:
            try:
                role = message.guild.get_role(self.emoji_role[str(payload.emoji)])
                # role = utils.get(message.guild.roles, id=self.emoji_role[str(payload.emoji)])
                if self.role_remove is True:
                    if role in member.roles:
                        await member.remove_roles(role)

                    else:
                        await member.add_roles(role)
            except KeyError:
                await message.remove_reaction(payload.emoji, payload.member)
            except Exception:
                traceback.print_exc()
        await message.remove_reaction(payload.emoji, payload.member)

    def start(self):
        self.bot.add_listener(self.on_raw_reaction_add, name='on_raw_reaction_add')
        self.bot.add_listener(self.on_ready, name='on_ready')
        self.bot.add_listener(self.on_member_join, name='on_member_join')