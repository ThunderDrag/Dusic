import discord
from discord.ext import commands
from modules.helper.types import Music


async def added_to_queue(name, spotify_url, queue_position, author_id, thumbnail_url) -> discord.Embed:
    embed = discord.Embed(title=f"**Added to Queue**", color=0x0061FF)
    embed.set_author(name="Music Queue")

    embed.add_field(
        name="**Music Name**", value=f"[{name}]({spotify_url})", inline=False
    )
    embed.add_field(
        name="**Queue Position**", value=f"{queue_position}", inline=False
    )
    embed.add_field(
        name="**Requested By**", value=f"<@{author_id}>", inline=False
    )
    embed.set_thumbnail(url=f"{thumbnail_url}")

    return embed


async def now_playing(music: Music) -> discord.Embed:
    embed = discord.Embed(title=f"**NOW PLAYING**", color=0x0061FF)
    embed.set_author(name="Music Player")

    embed.add_field(
        name="**Music Name**", value=f"[{music.name}]({music.spotify_url})", inline=False
    )
    embed.add_field(
        name="**Requested By**", value=f"<@{music.context.author.id}>", inline=False
    )
    embed.set_thumbnail(url=f"{music.thumbnail_url}")

    return embed


async def queue_completed() -> discord.Embed:
    embed = discord.Embed(title=f"**Queue Completed**", color=0x0061FF)
    embed.set_author(name="Music Queue")
    embed.description = "The queue has been completed. You can add more songs to the queue or start a new playlist."

    return embed


async def paused_music(music: Music, ctx: commands.Context) -> discord.Embed:
    embed = discord.Embed(title=f"**Music Paused**", color=0x0061FF)
    embed.set_author(name="Music Player")
    embed.description = f"**{music.name}** has been paused."
    embed.add_field(name="Requested By:", value=f"<@{ctx.author.id}>", inline=False)
    embed.set_thumbnail(url=f"{music.thumbnail_url}")

    return embed


async def resumed_music(music: Music, ctx: commands.Context) -> discord.Embed:
    embed = discord.Embed(title=f"**Music Resumed**", color=0x0061FF)
    embed.set_author(name="Music Player")
    embed.description = f"**{music.name}** has been resumed."
    embed.add_field(name="Requested By:", value=f"<@{ctx.author.id}>", inline=False)
    embed.set_thumbnail(url=f"{music.thumbnail_url}")

    return embed


async def skipped_music(music: Music, ctx: commands.Context) -> discord.Embed:
    embed = discord.Embed(title=f"**Skipped Song**", color=0x0061FF)
    embed.set_author(name="Music Player")
    embed.description = f"**{music.name}** has been skipped."
    embed.add_field(name="Requested By:", value=f"<@{ctx.author.id}>", inline=False)
    embed.set_thumbnail(url=f"{music.thumbnail_url}")

    return embed


async def afk() -> discord.Embed:
    embed = discord.Embed(title=f"**Left Voice Channel**", color=0x0061FF)
    embed.set_author(name="Music Player")
    embed.description = "I left the voice channel due to inactivity."

    return embed


async def cleared_queue(ctx: commands.Context) -> discord.Embed:
    embed = discord.Embed(title=f"**Queue Cleared**", color=0x0061FF)
    embed.set_author(name="Music Player")
    embed.description = "The music queue has been cleared."
    embed.add_field(name="Requested By:", value=f"<@{ctx.author.id}>", inline=False)

    return embed


async def left_channel(ctx: commands.Context) -> discord.Embed:
    embed = discord.Embed(title=f"**Left Channel**", color=0x0061FF)
    embed.set_author(name="Music Player")
    embed.description = "I left the voice channel."
    embed.add_field(name="Requested By:", value=f"<@{ctx.author.id}>", inline=False)

    return embed


async def no_music_playing() -> discord.Embed:
    embed = discord.Embed(title=f"**No Music Playing**", color=0x0061FF)
    embed.set_author(name="Music Player")
    embed.description = "There is no music playing at the moment."

    return embed