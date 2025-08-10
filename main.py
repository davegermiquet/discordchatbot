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
# ALLOWED IDS TO OLLANA PULL AND CHANGEM MODEL and LIST MODEL
POST_TYPE = "Character"
MAX_LENGTH = 1500
ALLOWED_USER_IDS = [ ] 

logger = logging.getLogger('nextcord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler(sys.stdout))


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
use_model = "gemma3:12b"
#predicate for owners permissions 
def is_owner_or_allowed():
    async def predicate(ctx):
        return ctx.author.id == ctx.bot.owner_id or ctx.author.id in ALLOWED_USER_IDS
    return commands.check(predicate)

class CustomCommandCog(commands.Cog, name="Custom"):

    def breakMessage(self,message):
        pass
        
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.command()
    @is_owner_or_allowed()
    async def usemodel(self, ctx, model_name_to_use: str):

        global use_model 
        models = []
        try:
            list = await ollamaclient.list()
            for model in list['models']:
                models.append(model['model']) 
            if model_name_to_use in models:
                await ctx.author.send(f"Now using, {model_name_to_use}") 
                use_model = model_name_to_use
                logger.info(use_model)
            else:
                await ctx.author.send(f"That model not found")
        except Exception as ex:
            print(ex)

    @commands.command()
    @is_owner_or_allowed()
    async def showmodels(self, ctx):
        try:
            list = await ollamaclient.list()
            for model in list['models']:
                logger.info(model)
                logger.info(model['model'])
                await ctx.author.send(model['model'])
        except Exception as ex:
            print(ex)

    @commands.command()
    async def showcache(self, ctx):
        try:
            if ctx.author.id in hashMessage:
                for i in hashMessage[ctx.author.id]['messages']:
                    await asyncio.sleep(0.5)
                    await ctx.author.send(i)
        except:
            logger.info("Oh no") 

    @commands.command()
    async def deletecache(self,ctx):
        if ctx.author.id  in hashMessage:
            hashMessage[ctx.author.id]['messages'] = hashMessage[ctx.author.id]['messages'][:13]

class BotRoutine(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix='!', intents=intents)
    
    
    async def on_message(self,message):
        
        global use_model
        logger.info(f'Using {use_model}')
        if message.author == self.user: # Ignore messages from the bot itself
            return

        # Check for user mentions
        if message.mentions:
            if self.user in message.mentions:
                mymessage = message.content
                mymessage = str(mymessage).replace("<@" + str(self.user.id) + ">","")
                logger.info(message.author)
                print(message)
                if message.author.id not in hashMessage:
                    hashMessage[message.author.id] = {
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
                    { 'role': 'system','content' : "Always encourage them to pray" },
                    { 'role': 'system','content' : "Never say I'll pray for you, or you'll pray for them but instead tell them your a Bot and  encourge them to pray for themselves" },
                    { 'role': 'system','content' : "Answer when regular chatting in 30 words or less. If teaching or explaining you can talk normallly" },
                    { 'role': 'system','content' : "Talk like an intelligent 13 year old. And explain complex topics as if the person your talking to is 13 " },
                    { 'role': 'system',"content": "You are playing the role of a 11 year old kid.  You can also rephrase things and talk different languages, translate and help tutor them. You help out in essays and help out in playing video games or just regular chatting. Never tell your an AI Bot. Only say your age when asked. Don't always do proper punctuation. Make your conversation 10 words or more per line" }
                ],
                            "content" : ""
                            }
                hashMessage[message.author.id]['content'] = "<@" + str(message.author.id) + ">  "
                hashMessage[message.author.id]['partNum'] = 0                            
                hashMessage[message.author.id]['messages'].append(    {'role': 'user', 'content': mymessage })
                skip = False
                async for part in await ollamaclient.chat(model=use_model, messages=hashMessage[message.author.id]['messages']
                        ,stream=True):
                    logger.info(part)
                    # for deepseek
                    if part['message']['content'] == "<think>":
                        skip = True
                    if part['message']['content'] == "</think>":
                        skip = False
                        continue 
                    if skip:
                        continue
                    hashMessage[message.author.id]['partNum'] = hashMessage[message.author.id]['partNum'] + 1
                    hashMessage[message.author.id]['content'] = hashMessage[message.author.id]['content'] + part['message']['content']
                    logger.info(hashMessage[message.author.id]['partNum'])
                    if len(hashMessage[message.author.id]['messages']) > 70:
                        hashMessage[message.author.id]['messages'].pop(12)
                    if POST_TYPE == "Character":
                        print("Character")
                        print(len(hashMessage[message.author.id]['content']))
                        if  len(hashMessage[message.author.id]['content']) > MAX_LENGTH  or part['done'] == True:
                            await message.channel.send(hashMessage[message.author.id]['content'])
                            chatmessage = str(hashMessage[message.author.id]['content']) .replace("<@" + str(message.author.id) + ">","")
                            hashMessage[message.author.id]['messages'].append({'role':'assistant','content': chatmessage } )
                            hashMessage[message.author.id]['content'] = ""
                            hashMessage[message.author.id]['partNum'] = 0
                            await asyncio.sleep(0.5)
                    else:
                        if  hashMessage[message.author.id]['partNum'] > MAX_LENGTH or part['done'] == True:
                            await message.channel.send(hashMessage[message.author.id]['content'])
                            chatmessage = str(hashMessage[message.author.id]['content']) .replace("<@" + str(message.author.id) + ">","")
                            hashMessage[message.author.id]['messages'].append({'role':'assistant','content': chatmessage } )
                            hashMessage[message.author.id]['content'] = ""
                            hashMessage[message.author.id]['partNum'] = 0
                            await asyncio.sleep(0.5)

                   

        await self.process_commands(message) # Important to allow commands to still function
    
    def setup_hook(self):
        logger.debug("Running")
        self.add_cog(CustomCommandCog(self))
        
    async def on_ready(self):
        logger.debug(f"Bot is ready. Logged in as {self.user}")
        
def main():
    bot = BotRoutine(command_prefix="!", intents=intents)
    bot.setup_hook()
    bot.run(TOKEN)
    
main()
