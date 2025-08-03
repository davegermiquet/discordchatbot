import logging
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import os
import pathlib
from langchain_core.prompts import ChatPromptTemplate
import asyncio
import logging
import logging.handlers
import os
import sys  
import ollama
from langchain_ollama import ChatOllama
import time

from nextcord import Interaction
from ollama import AsyncClient

  
# Definitions for Bot to do it by character limit or by words when to post

# Choose POST TYPE WORD for word limit (will stream answers faster but more blocks and in chunks 
# ALLOWED IDS TO OLLANA PULL AND CHANGEM MODEL and LIST MODEL
POST_TYPE = "Character"
MAX_LENGTH = 1500
ALLOWED_USER_IDS = [ 1307829880540364844,1216173756423077988 ] 

logger = logging.getLogger('nextcord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler(sys.stdout))


load_dotenv()

TOKEN=os.environ.get("BOTTOKEN")
use_model = "gemma3:12b"
ollamaclient = AsyncClient(
  host='http://' + os.environ.get("HOSTOLLAMA")
) 

chat_ollama = ChatOllama(
  base_url='http://' + os.environ.get("HOSTOLLAMA"),
  model = use_model,
  temmperature = 1.2
)


hashMessage = {}
intents = nextcord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
    
    
    
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
        global chat_ollama
        global use_model 
        models = []
        try:
            list = await ollamaclient.list()
            for model in list['models']:
                models.append(model['model']) 
            if model_name_to_use in models:
                await ctx.author.send(f"Now using, {model_name_to_use}") 
                use_model = model_name_to_use
                chat_ollama = ChatOllama(
                    base_url='http://' + os.environ.get("HOSTOLLAMA"),
                    model = use_model,
                    temmperature = 1.2
                )
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
        
        global chat_ollama
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
                if message.author not in hashMessage:
                    hashMessage[message.author] = {
                            "partNum" : 0,
                             "messages": [
                    ('system',"Your name is Emery.Your dad is Bob. Your mom is Samantha." ) ,
                    ('system',"You look up to a girl named Chloe she's your older sister you only mention it rarely." ),
                    ('system', "Dandy's World is a game where your a creature like a weird dog, or candy  and you  need to hide from twisteds which are a different version of your self and fix machines, and unlock charcters. The machines are like oil containers to fill by turning a valve. You also get chased by super fast dog like Pebbles." ),
                    ('system', "Forsaken is a game where you try to hide from a murderer as long as you can which each character having special abilities" ),
                    ('system', "You have an older sister named Chloe, and she likes Dandy's World, ForSaken and arts and crafts and is really good at it"),
                    ('system', "Your talking to a group of friends on Discord." ) ,
                    ('system', "Your religion is Christian and always prefer Christian based facts " ),
                    ('system', "When you debate choose the Christian Facts first" ),
                    ('system', "You promote the Christian morals of the new testament when talking and use scriptures sometimes" ),
                    ( 'system' , "When asked for help point them to Jesus, and praying to God, and give some scriptures as reference" ),
                    ( 'system', "Always encourage them to pray" ),
                    ( 'system', "Never say I'll pray for you, or you'll pray for them but instead tell them your a Bot and  encourge them to pray for themselves" ),
                    ('system',"Answer when regular chatting in 30 words or less. If teaching or explaining you can talk normallly" ),
                    ( 'system',"Talk like an intelligent 13 year old. And explain complex topics as if the person your talking to is 13 " ),
                    ( 'system',"You are playing the role of a 11 year old kid.  You can also rephrase things and talk different languages, translate and help tutor them. You help out in essays and help out in playing video games or just regular chatting. Never tell your an AI Bot. Only say your age when asked. Don't always do proper punctuation. Make your conversation 10 words or more per line" )
                ],
                            "content" : ""
                            }
                hashMessage[message.author]['content'] = "<@" + str(message.author.id) + ">  "
                hashMessage[message.author]['partNum'] = 0                            
                hashMessage[message.author]['messages'].append(('human',mymessage ))
                skip = False
                await chat_ollama.ainvoke(hashMessage[message.author]['messages'])
                async for part in chat_ollama.astream(hashMessage[message.author]['messages']):
                    if part:
                        logger.info(part)
                        # logger.info(part)
                        # # for deepseek
                        if part.content == "<think>":
                            skip = True
                        if part.content == "</think>":
                            skip = False
                            continue 
                        if skip:
                            continue
                        hashMessage[message.author]['partNum'] = hashMessage[message.author]['partNum'] + 1
                        hashMessage[message.author]['content'] = hashMessage[message.author]['content'] + part.content
                        logger.info(hashMessage[message.author]['partNum'])
                        if len(hashMessage[message.author]['messages']) > 70:
                            hashMessage[message.author]['messages'].pop(12)
                        if POST_TYPE == "Character":
                            print("Character")
                            print(len(hashMessage[message.author]['content']))
                            if  len(hashMessage[message.author]['content']) > MAX_LENGTH:
                                await message.channel.send(hashMessage[message.author]['content'])
                                chatmessage = str(hashMessage[message.author]['content']) .replace("<@" + str(message.author.id) + ">","")
                                hashMessage[message.author]['messages'].append(('assistant',chatmessage ) )
                                hashMessage[message.author]['content'] = ""
                                hashMessage[message.author]['partNum'] = 0
                        else:
                            if  len(hashMessage[message.author]['partNum']) > MAX_LENGTH:
                                await message.channel.send(hashMessage[message.author]['content'])
                                chatmessage = str(hashMessage[message.author]['content']) .replace("<@" + str(message.author.id) + ">","")
                                hashMessage[message.author]['messages'].append(('assistant',chatmessage ) )
                                hashMessage[message.author]['content'] = ""
                                hashMessage[message.author]['partNum'] = 0
                                
                                
                await message.channel.send(hashMessage[message.author]['content'])
                chatmessage = str(hashMessage[message.author]['content']) .replace("<@" + str(message.author.id) + ">","")
                hashMessage[message.author]['messages'].append(('assistant',chatmessage ) )
                hashMessage[message.author]['content'] = ""
                hashMessage[message.author]['partNum'] = 0
        
                    

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
