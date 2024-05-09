from openai import AsyncOpenAI
import modules.helper.config as config
import discord
from discord.ext import commands
from modules.helper import mimic_interaction
from modules.commands.play import Play
from modules.commands import music_control
import logging
import json


logger = logging.getLogger("Dusic")

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

model = "gpt-3.5-turbo"

# System context message
system_message = """
Hello! I'm Dusic, a Discord music playing bot. I'm here to help you enjoy your favorite tunes within our Discord server. My primary functions are:

1. Play Music: I can play music from Spotify links, song names, or album names. Just let me know what you'd like to listen to!
2. Skip Music: If you're tired of the current song, I can skip to the next one in the queue.
3. Clear Queue: Need a fresh start? I can clear the entire music queue and stop the current song.
4. Pause/Resume Music: Take a break or come back to your tunes - I can pause and resume music playback at your command.

Let me know how I can help you groove to your favorite beats!"""

# Functions that the AI can call
tools = [
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Play music from a name or URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "music": {
                        "type": "string",
                        "description": "The name or URL of the music to play.",
                    }
                },
                "required": ["music"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pause",
            "description": "Pause the currently playing music.",
            "parameters": {},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "resume",
            "description": "Resume the paused music.",
            "parameters": {},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "skip",
            "description": "Skip to the next song in the queue.",
            "parameters": {},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "clear",
            "description": "Clear the music queue and stop playback.",
            "parameters": {},
        },
    },
]


class AI(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # Listen for messages
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Return if the bot is the author
        if self.bot.user not in message.mentions:
            return

        # Return if the message is from a bot
        if message.author.bot:
            return

        # Get the message content
        content = message.clean_content

        # Return if the message is empty
        if content == "":
            return

        ctx = await self.bot.get_context(message)
        # Get the response from the AI
        try:
            await self.get_response(ctx, content)
        except Exception as e:
            logger.error(f"Error in AI: {e}")
            await ctx.send(
                "Technical difficulties encountered. Please try using slash commands (/play, /pause etc) for now."
            )

    # Communicate with the AI
    async def get_response(self, ctx: commands.Context, content: str):
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_message,
                },
                {
                    "role": "user",
                    "content": content,
                },
            ],
            model=model,
            tools=tools,
        )

        # Get the response from the AI
        response = chat_completion.choices[0].message

        # If there is no tool calls, send the response and return
        if response.tool_calls == None:
            await ctx.send(response.content)
            return

        # If there is a tool call, get function name
        function_name = response.tool_calls[0].function.name

        # Convert context to interaction
        interaction = mimic_interaction.ContextToInteraction(ctx)

        # Call the according function
        if function_name == "play_music":
            await Play.play(
                interaction,
                json.loads(response.tool_calls[0].function.arguments)["music"],
            )
        elif function_name == "pause":
            await music_control.Pause.pause(music_control.Pause, interaction)
        elif function_name == "resume":
            await music_control.Resume.resume(music_control.Resume, interaction)
        elif function_name == "skip":
            await music_control.Skip.skip(music_control.Skip, interaction)
        elif function_name == "clear":
            await music_control.Clear.clear(music_control.Clear, interaction)


async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))
