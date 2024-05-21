import openai
import discord
import json
import logging
from modules.helper import config
from discord.ext import commands
from openai.types.chat import ChatCompletionMessage
from modules.commands import play
from modules.commands.music_commands import Resume, Pause, Skip, Clear, Leave

# Setup Logger
logger = logging.getLogger(config.LOGGER_NAME)

# Create a OpenAI instance
openai_client = openai.AsyncOpenAI(api_key=config.OPENAI_API_KEY)

model = "gpt-3.5-turbo"


system_message = """
You are an discord bot, your name is Dusic and your job is to play music on discord servers.

You can play music from Spotify links, song names, or album names. You can skip songs, clear the queue, leave the channel, pause and resume music playback.

1. Play Music: I can play music from Spotify links, song names, or album names. Just let me know what you'd like to listen to!
2. Skip Music: If you're tired of the current song, I can skip to the next one in the queue.
3. Clear Queue: Need a fresh start? I can clear the entire music queue and stop the current song.
4. Pause/Resume Music: Take a break or come back to your tunes - I can pause and resume music playback at your command.
5. Leave Channel: If you're done listening to music, I can leave the voice channel.
"""


# Functions that the AI can call
tools = [
    {
        "type": "function",
        "function": {
            "name": "play",
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
            "description": "Clear the music queue and stop playback",
            "parameters": {},
        },
    },
        {
        "type": "function",
        "function": {
            "name": "leave",
            "description": "Leave the voice channel and stop playback",
            "parameters": {},
        },
    },
]


class AI(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    # Function to wait for a message to come
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Return if bot isn't mentioned or the message is from bot
        if self.bot.user not in message.mentions:
            return
        
        if message.author.bot:
            return
        
        # Get the message content
        content = message.clean_content
        
        # Get the context
        ctx = await self.bot.get_context(message)
        
        # Fetch the response from GPT and then send it
        try:
            response = await self.fetch_gpt_response(content)
            await self.reply(ctx, response)
        except Exception as e:
            logger.error(f"Error while fetching GPT response: {e}")
            await ctx.send("An error occurred while working on your request. Please try again later.")
    
        
    # Function to fetch response from GPT
    async def fetch_gpt_response(self, content: str):
        chat_completion = await openai_client.chat.completions.create(
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
        
        return response
    
    async def reply(self, ctx: commands.Context, response: ChatCompletionMessage):
        # If the response is just a message, then send it and return
        if response.tool_calls == None:
            await ctx.send(response.content)
            return
        
        # If there is a tool call, get function name
        function_name = response.tool_calls[0].function.name
        
        if(function_name == "play"):
            await play.play(ctx, json.loads(response.tool_calls[0].function.arguments)["music"])
        elif(function_name == "pause"):
            await Pause.pause(ctx)
        elif(function_name == "resume"):
            await Resume.resume(ctx)
        elif(function_name == "skip"):
            await Skip.skip(ctx)
        elif(function_name == "clear"):
            await Clear.clear(ctx)
        elif(function_name == "leave"):
            await Leave.leave(ctx)



async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))