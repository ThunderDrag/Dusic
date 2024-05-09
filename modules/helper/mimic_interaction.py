from discord.ext import commands
import discord


class ContextToInteraction:
    class Followup:
        def __init__(self, ctx: commands.Context):
            self.ctx = ctx

        async def send(self, *args, **kwargs):
            return await self.ctx.reply(*args, **kwargs)

    class Response:
        def __init__(self, ctx: commands.Context):
            self.ctx = ctx

        async def defer(self):
            await self.ctx.defer()

    class Channel:
        def __init__(self, ctx: commands.Context):
            self.ctx = ctx

        async def send(self, *args, **kwargs):
            return await self.ctx.send(*args, **kwargs)

    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.followup = self.Followup(ctx)
        self.response = self.Response(ctx)
        self.channel = self.Channel(ctx)

    @property
    def user(self):
        return self.ctx.author

    @property
    def guild_id(self):
        return self.ctx.guild.id


commands.Context
discord.Interaction
