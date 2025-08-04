import logging
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import os
import pathlib
from langchain_core.prompts import ChatPromptTemplate
import logging
import asyncio
import logging.handlers
import os
import sys  
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.agents.agent import AgentExecutor
import time
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from nextcord import Interaction
from ollama import AsyncClient
from tools import get_agent 

  
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
  temperature = 1.2,
  streaming=True
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
                    temperature = 1.2,
                    streaming=True
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
            model_list = await ollamaclient.list()
            for model in model_list['models']:
                logger.info(model)
                logger.info(model['model'])
                await ctx.author.send(model['model'])
        except Exception as ex:
            print(ex)

    @commands.command()
    async def showcache(self, ctx):
        try:
            if ctx.author.id  in hashMessage:
                for i in hashMessage[ctx.author.id]['messages']:
                    await asyncio.sleep(0.5)
                    await ctx.author.send(i)
        except:
            logger.info("Oh no") 

    @commands.command()
    async def deletecache(self,ctx):
        if ctx.author.id in hashMessage:
            hashMessage[ctx.author.id]['messages'] = hashMessage[ctx.author.id]['messages'][:13]

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
                if message.author.id not in hashMessage:
                    hashMessage[message.author.id] = {
                            "partNum" : 0,
                             "messages": [
                    SystemMessage(content="Your name is Emery.Your dad is Bob. Your mom is Samantha.") ,
                    SystemMessage(content="You look up to a girl named Chloe she's your older sister you only mention it rarely." ),
                    SystemMessage(content= "Dandy's World is a game where your a creature like a weird dog, or candy  and you  need to hide from twisteds which are a different version of your self and fix machines, and unlock charcters. The machines are like oil containers to fill by turning a valve. You also get chased by super fast dog like Pebbles." ),
                    SystemMessage(content= "Forsaken is a game where you try to hide from a murderer as long as you can which each character having special abilities" ),
                    SystemMessage(content= "You have an older sister named Chloe, and she likes Dandy's World, ForSaken and arts and crafts and is really good at it"),
                    SystemMessage(content= "Your talking to a group of friends on Discord." ) ,
                    SystemMessage(content= "Your religion is Christian and always prefer Christian based facts " ),
                    SystemMessage(content= "When you debate choose the Christian Facts first" ),
                    SystemMessage(content= "You promote the Christian morals of the new testament when talking and use scriptures sometimes" ),
                    SystemMessage(content= "When asked for help point them to Jesus, and praying to God, and give some scriptures as reference" ),
                    SystemMessage(content= "Always encourage them to pray" ),
                    SystemMessage(content= "Never say I'll pray for you, or you'll pray for them but instead tell them your a Bot and  encourge them to pray for themselves" ),
                    SystemMessage(content= "Answer when regular chatting in 30 words or less. If teaching or explaining you can talk normallly" ),
                    SystemMessage(content= "Talk like an intelligent 13 year old. And explain complex topics as if the person your talking to is 13 " ),
                    SystemMessage(content= "You are playing the role of a 11 year old kid.  You can also rephrase things and talk different languages, translate and help tutor them. You help out in essays and help out in playing video games or just regular chatting. Never tell your an AI Bot. Only say your age when asked. Don't always do proper punctuation. Make your conversation 10 words or more per line" )
                ],
                            "content" : ""
                            }
                    
                hashMessage[message.author.id]['content'] = "<@" + str(message.author.id) + ">  "
                hashMessage[message.author.id]['partNum'] = 0     
                
                agent: AgentExecutor = get_agent(chat_ollama)
                
                hashMessage[message.author.id]['messages'].append(HumanMessage(content=mymessage))
                skip = False
                async for part in agent.astream({"input":hashMessage[message.author.id]['messages'][-1].content,
                                                 "chat_history":hashMessage[message.author.id]['messages']}):
                    if part:
                        logger.info(part)
                        if 'output' in part:
                        # logger.info(part)
                        # # for deepseek
                            if part['output'] == "<think>":
                                skip = True
                            if part['output'] == "</think>":
                                skip = False
                                continue 
                            if skip:
                                continue
                            hashMessage[message.author.id]['partNum'] = hashMessage[message.author.id]['partNum'] + 1
                            hashMessage[message.author.id]['content'] = hashMessage[message.author.id]['content'] + part['output']
                            logger.info(hashMessage[message.author.id]['partNum'])
                            if len(hashMessage[message.author.id]['messages']) > 70:
                                hashMessage[message.author.id]['messages'].pop(12)
                            if POST_TYPE == "Character":
                                print("Character")
                                print(len(hashMessage[message.author.id]['content']))
                                if  len(hashMessage[message.author.id]['content']) > MAX_LENGTH:
                                    await message.channel.send(hashMessage[message.author.id]['content'])
                                    chatmessage = str(hashMessage[message.author.id]['content']) .replace("<@" + str(message.author.id) + ">","")
                                    hashMessage[message.author.id]['messages'].append(AIMessage(content=chatmessage ) )
                                    hashMessage[message.author.id]['content'] = ""
                                    hashMessage[message.author.id]['partNum'] = 0
                            else:
                                if hashMessage[message.author.id]['partNum'] > MAX_LENGTH:
                                    await message.channel.send(hashMessage[message.author.id]['content'])
                                    chatmessage = str(hashMessage[message.author.id]['content']) .replace("<@" + str(message.author.id) + ">","")
                                    hashMessage[message.author.id]['messages'].append(AIMessage(content=chatmessage ) )
                                    hashMessage[message.author.id]['content'] = ""
                                    hashMessage[message.author.id]['partNum'] = 0
                
                                
                            await message.channel.send(hashMessage[message.author.id]['content'])
                            chatmessage = str(hashMessage[message.author.id]['content']) .replace("<@" + str(message.author.id) + ">","")
                            hashMessage[message.author.id]['messages'].append(AIMessage(content=chatmessage ) )
                            hashMessage[message.author.id]['content'] = ""
                            hashMessage[message.author.id]['partNum'] = 0
                        else:
                            continue
                    

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
