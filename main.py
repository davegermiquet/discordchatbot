import logging
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import os
import pathlib

import asyncio
import logging
import logging.handlers
import os
import sys  
import ollama
import time

from nextcord import Interaction

logger = logging.getLogger('nextcord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler(sys.stdout))

# Assume client refers to a discord.Client subclass...

load_dotenv()

TOKEN=os.environ.get("BOTTOKEN")
from ollama import AsyncClient
ollamaclient = AsyncClient(
  host='http://' + os.environ.get("HOSTOLLAMA")
)

intents = nextcord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True


class CustomCommandCog(commands.Cog, name="Custom"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.command()
    async def bumpme(self, ctx):
        await ctx.send('/bump')

    @commands.command()
    async def saysomething(self, ctx):
        await ctx.send('hello im here')



class BotRoutine(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix='!', intents=intents)
    
    
    async def on_message(self,message):
        
        if message.author == self.user: # Ignore messages from the bot itself
            return

        # Check for user mentions
        if message.mentions:
            if self.user in message.mentions:
                mymessage = message.content
                mymessage = str(mymessage).replace("<@" + str(self.user.id) + ">","")
                logger.info(mymessage)
                logger.info(self.user.id)
                content = ""
                numOfPart = 0
                async for part in await ollamaclient.chat(model='ollama.com/library/llama3.2:latest', messages=[{'role': 'user', 'content': mymessage }],stream=True):
                    numOfPart = numOfPart + 1
                    content = content + part['message']['content']
                    logger.info(part['message']['content'])
                    logger.info(message)
                    if numOfPart == 100 or part['message']['content'] == "":
                        await message.channel.send(content)
                        logger.info(content)
                        numOfPart = 0
                        content = ""
                        time.sleep(1)
                   

        await self.process_commands(message) # Important to allow commands to still function
    
    def setup_hook(self):
        logger.debug("Running")
        self.add_cog(CustomCommandCog(self))
        
    async def on_ready(self):
        logger.debug(f"Bot is ready. Logged in as {self.user}")

        # Get a channel by ID (recommended way)
        channel_id = 1346631689073459303
        channel = await self.fetch_channel(channel_id)
        await channel.send ("Connected with the following commands")
        if channel:
            cog = self.get_cog("Custom")
            for i in cog.get_commands():
                await channel.send(i)
            pass
        else:
            logger.debug("Channel not found.")
            
def main():
    bot = BotRoutine(command_prefix="!", intents=intents)
    bot.setup_hook()
    bot.run(TOKEN)
    
main()