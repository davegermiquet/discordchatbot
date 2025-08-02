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
hashMessage = {}
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
                logger.info(message.author)
                if message.author not in hashMessage:
                    hashMessage[message.author] = {
                            "partNum" : 0,
                             "messages": [
                    { 'role': 'system',"content": "Your name is John.You look up to a girl named Dasia she's like your older sister you only mention it rarely. Your talking to a group of friends on Discord.  You are playing the role of a 13 year old kid.  You can also rephrase things and talk different languages, translate and help tutor them. You help out in essays and help out in playing video games or just regular chatting. Never tell your an AI Bot. Only say your age when asked. Don't always do proper punctuation.Only write paragraphs and sentences for answers minimal new lines unless giving code. Make your conversation 10 words or more per line " }
                ],
                            "content" : ""
                            }
                hashMessage[message.author]['content'] = "<@" + str(message.author.id) + ">  "
                hashMessage[message.author]['partNum'] = 0                            
                hashMessage[message.author]['messages'].append(    {'role': 'user', 'content': mymessage })
                async for part in await ollamaclient.chat(model='gemma3:12b', messages=hashMessage[message.author]['messages']
                        ,stream=True):
                    hashMessage[message.author]['partNum'] = hashMessage[message.author]['partNum'] + 1
                    hashMessage[message.author]['content'] = hashMessage[message.author]['content'] + part['message']['content']
                    logger.info(part['message']['content'])
                    logger.info(part)
                    logger.info(message)
                    #hashMessage[message.author]['messages'].append(part['message'])
                    logger.info(hashMessage[message.author]['partNum'])
                    if len(hashMessage[message.author]['messages']) > 50:
                        hashMessage[message.author]['messages'].pop(1)
                    if  hashMessage[message.author]['partNum'] > 60 or part['done'] == True:
                        await message.channel.send(hashMessage[message.author]['content'])
                        chatmessage = str(hashMessage[message.author]['content']) .replace("<@" + str(message.author.id) + ">","")
                        hashMessage[message.author]['messages'].append({'role':'assistant','content': chatmessage } )
                        logger.info(hashMessage[message.author]['content'])
                        hashMessage[message.author]['content'] = ""
                        hashMessage[message.author]['partNum'] = 0
                        logger.info(hashMessage[message.author]['partNum'])
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
