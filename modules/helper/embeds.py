import discord
from modules.helper.class_types import Music


async def added_to_queue(music: Music) -> discord.Embed:
    embed = discord.Embed(title=f"Added {music.type} to Queue", color=0x0061FF)

    embed.add_field(
        name="Name", value=f"> [{music.name}]({music.spotify_url})", inline=False
    )
    embed.add_field(
        name="Queue Position", value=f"> {music.queue_position}", inline=False
    )
    embed.add_field(
        name="Requested By:", value=f"> <@{music.interaction.user.id}>", inline=False
    )
    embed.set_thumbnail(url=f"{music.thumbnail}")

    return embed


async def now_playing_embed(music: Music) -> discord.Embed:
    embed = discord.Embed(title=f"NOW PLAYING", color=0x0061FF)

    embed.add_field(
        name="Name", value=f"> [{music.name}]({music.spotify_url})", inline=False
    )
    embed.add_field(
        name="Requested By:", value=f"> <@{music.interaction.user.id}>", inline=False
    )
    embed.set_thumbnail(url=f"{music.thumbnail}")

    return embed


async def queue_completed_embed() -> discord.Embed:
    embed = discord.Embed(title=f"Queue Completed", color=0x0061FF)
    embed.description = "Queue has been completed."

    return embed
