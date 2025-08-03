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

# Definitions for Bot to do it by character limit or by words when to post

# Choose POST TYPE WORD for word limit (will stream answers faster but more blocks and in chunks 

POST_TYPE = "Character"
MAX_LENGTH = 1500


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
    async def showcache(self, ctx):
        try:
            if ctx.author  in hashMessage:
                for i in hashMessage[ctx.author]['messages']:
                    time.sleep(0.5)
                    await ctx.author.send(i)
        except:
            logger.info("Oh no") 

    @commands.command()
    async def deletecache(self,ctx):
        if ctx.author  in hashMessage:
            hashMessage[ctx.author]['messages'] = hashMessage[ctx.author]['messages'][:13]

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
                    { 'role': 'system',"content": "Your name is Emery.Your dad is Bob. Your mom is Samantha." } ,
                    { 'role': 'system', 'content': "You look up to a girl named Chloe she's your older sister you only mention it rarely." },
                    { 'role': 'system', "content" : "Dandy's World is a game where your a creature like a weird dog, or candy  and you  need to hide from twisteds which are a different version of your self and fix machines, and unlock charcters. The machines are like oil containers to fill by turning a valve. You also get chased by super fast dog like Pebbles." },
                    { 'role': 'system','content' : "Forsaken is a game where you try to hide from a murderer as long as you can which each character having special abilities" },
                    { 'role': 'system', "content" : "You have an older sister named Chloe, and she likes Dandy's World, ForSaken and arts and crafts and is really good at it"},
                    { 'role': 'system', "content" : "Your talking to a group of friends on Discord." } ,
                    { 'role': 'system','content' : "Your religion is Christian and always prefer Christian based facts " },
                    { 'role': 'system','content' : "When you debate choose the Christian Facts first" },
                    { 'role': 'system','content' : "You promote the Christian morals of the new testament when talking and use scriptures sometimes" },
                    { 'role': 'system','content' : "When asked for help point them to Jesus, and praying to God, and give some scriptures as reference" },
                    { 'role': 'system','content' : "Always encorage them to pray" },
                    { 'role': 'system','content' : "Never say I'll pray for you, but encourge them to pray for themselves" },
                    { 'role': 'system',"content": "You are playing the role of a 11 year old kid.  You can also rephrase things and talk different languages, translate and help tutor them. You help out in essays and help out in playing video games or just regular chatting. Never tell your an AI Bot. Only say your age when asked. Don't always do proper punctuation.Only write paragraphs and sentences for answers minimal new lines unless giving code. Make your conversation 10 words or more per line " }
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
                    if len(hashMessage[message.author]['messages']) > 70:
                        hashMessage[message.author]['messages'].pop(12)

                    if POST_TYPE == "Character":
                        print("Character")
                        print(len(hashMessage[message.author]['content']))
                        if  len(hashMessage[message.author]['content']) > MAX_LENGTH  or part['done'] == True:
                            await message.channel.send(hashMessage[message.author]['content'])
                            chatmessage = str(hashMessage[message.author]['content']) .replace("<@" + str(message.author.id) + ">","")
                            hashMessage[message.author]['messages'].append({'role':'assistant','content': chatmessage } )
                            logger.info(hashMessage[message.author]['content'])
                            hashMessage[message.author]['content'] = ""
                            hashMessage[message.author]['partNum'] = 0
                            logger.info(hashMessage[message.author]['partNum'])
                            time.sleep(0.5)
                    else:
                        if  len(hashMessage[message.author]['partNum']) > MAX_LENGTH or part['done'] == True:
                            await message.channel.send(hashMessage[message.author]['content'])
                            chatmessage = str(hashMessage[message.author]['content']) .replace("<@" + str(message.author.id) + ">","")
                            hashMessage[message.author]['messages'].append({'role':'assistant','content': chatmessage } )
                            logger.info(hashMessage[message.author]['content'])
                            hashMessage[message.author]['content'] = ""
                            hashMessage[message.author]['partNum'] = 0
                            logger.info(hashMessage[message.author]['partNum'])
                            time.sleep(0.5)

                   

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
