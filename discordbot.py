import nextcord
from nextcord.ext import commands
import asyncio
from langchaintools import get_use_model
from langchaintools import set_use_model
from shared import create_chat_ollama
from shared import get_url_for_ollama
from shared import ALLOWED_USER_IDS
from shared import MAX_LENGTH
from langchaintools import get_agent
from shared import POST_TYPE
import base64
from langchain_core.messages import HumanMessage,AIMessage
import myprompts

def create_bot(ollamaclient,chat_ollama,logger): 
    intents = nextcord.Intents.default()
    intents.members = True
    intents.messages = True
    intents.guilds = True
    intents.message_content = True
    intents.presences = True
    bot = BotRoutine(command_prefix="!", intents=intents,ollamaclient=ollamaclient,chat_ollama=chat_ollama,logger=logger)
    return bot

#predicate for owners permissions 
def is_owner_or_allowed():
    async def predicate(ctx):
        return ctx.author.id == ctx.bot.owner_id or ctx.author.id in ALLOWED_USER_IDS
    return commands.check(predicate)

class CustomCommandCog(commands.Cog, name="Custom"):

    def breakMessage(self,message):
        pass
        
    def __init__(self, bot: commands.Bot,ollamaclient=None,chat_ollama=None,logger=None,hashMessage=None):
        self.ollamaclient = ollamaclient
        self.chat_ollama = chat_ollama
        self.logger = logger
        self.bot = bot
        self.hashMessage = hashMessage
        
    @commands.command()
    @is_owner_or_allowed()
    async def usemodel(self, ctx, model_name_to_use: str):
        global create_chat_ollama
        global get_use_model
        global set_use_model
        models = []
        try:
            list = await self.ollamaclient.list()
            for model in list['models']:
                models.append(model['model']) 
            if model_name_to_use in models:
                await ctx.author.send(f"Now using, {model_name_to_use}") 
                set_use_model(model_name_to_use)
                self.logger.info(get_use_model())
            else:
                await ctx.author.send(f"That model not found")
        except Exception as ex:
            print(ex)

    @commands.command()
    @is_owner_or_allowed()
    async def showmodels(self, ctx):
        try:
            model_list = await self.ollamaclient.list()
            for model in model_list['models']:
                self.logger.info(model)
                self.logger.info(model['model'])
                await ctx.author.send(model['model'])
        except Exception as ex:
            print(ex)

    @commands.command()
    async def showcache(self, ctx):
        try:
            if ctx.author.id  in self.hashMessage:
                for i in self.hashMessage[ctx.author.id]['messages']:
                    await asyncio.sleep(0.5)
                    await ctx.author.send(i)
        except:
            self.logger.info("Oh no") 

    @commands.command()
    async def deletecache(self,ctx):
        if ctx.author.id in self.hashMessage:
            self.hashMessage[ctx.author.id]['messages'] = self.hashMessage[ctx.author.id]['messages'] = []

class BotRoutine(commands.Bot):
    def __init__(self, command_prefix='!',intents=None,ollamaclient=None,chat_ollama=None,logger=None):
        self.ollamaclient = ollamaclient
        self.chat_ollama = chat_ollama
        self.logger = logger
        self.hashMessage = {}
        super().__init__(command_prefix=command_prefix, intents=intents)
    
    
    async def on_message(self,message):
        global get_use_model
        self.logger.info(f'Using {get_use_model()}')

        if message.author == self.user: # Ignore messages from the bot itself
            return

        # Check for user mentions
        if message.mentions:
            if self.user in message.mentions:
                self.chat_ollama = create_chat_ollama(
                    base_url=get_url_for_ollama(),
                    model = get_use_model(),
                    temperature = 1.2
                )
                mymessage = message.content
                mymessage = str(mymessage).replace("<@" + str(self.user.id) + ">","")
                self.logger.info(message.author)
                print(message)
                if message.author.id not in self.hashMessage:
                    self.hashMessage[message.author.id] = {
                            "partNum" : 0,
                             "messages": [ ],
                            "content" : ""
                            }
                    
                self.hashMessage[message.author.id]['content'] = "<@" + str(message.author.id) + ">  "
                self.hashMessage[message.author.id]['partNum'] = 0     
                
                agent = get_agent(self.chat_ollama,myprompts.system_message_prompt,{ "message": message, "bot" : self },self.logger)
                mycontent = []
                if message.attachments:
                    for attachment in message.attachments:
                        if attachment.content_type and attachment.content_type.startswith("image/"):
                            image_bytes = await attachment.read()
                            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                            mycontent.append({"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_base64}"})
                            
                mycontent.append({"type": "text","text":f"Question: {mymessage}"})  
                self.hashMessage[message.author.id]['messages'].append(HumanMessage(content=mycontent))

                skip = False
                async for part in agent.astream({ "input": self.hashMessage[message.author.id]['messages'][-1].content,"chat_history" : self.hashMessage[message.author.id]['messages']}):
                    if part:
                        self.logger.info(part)
                        if part.content:
                        # logger.info(part)
                        # # for deepseek
                            self.hashMessage[message.author.id]['partNum'] = self.hashMessage[message.author.id]['partNum'] + 1
                            self.hashMessage[message.author.id]['content'] = self.hashMessage[message.author.id]['content'] + part.content
                            self.logger.info(self.hashMessage[message.author.id]['partNum'])
                            if len(self.hashMessage[message.author.id]['messages']) > 30:
                                self.hashMessage[message.author.id]['messages'].pop(0)
                            if POST_TYPE == "Character":
                                print("Character")
                                print(len(self.hashMessage[message.author.id]['content']))
                                if  len(self.hashMessage[message.author.id]['content']) > MAX_LENGTH:
                                    await message.channel.send(self.hashMessage[message.author.id]['content'])
                                    chatmessage = str(self.hashMessage[message.author.id]['content']) .replace("<@" + str(message.author.id) + ">","")
                                    self.hashMessage[message.author.id]['messages'].append(AIMessage(content=chatmessage ) )
                                    self.hashMessage[message.author.id]['content'] = ""
                                    self.hashMessage[message.author.id]['partNum'] = 0
                            else:
                                if self.hashMessage[message.author.id]['partNum'] > MAX_LENGTH:
                     
                                    await message.channel.send(self.hashMessage[message.author.id]['content'])
                                    chatmessage = str(self.hashMessage[message.author.id]['content']) .replace("<@" + str(message.author.id) + ">","")
                                    self.hashMessage[message.author.id]['messages'].append(AIMessage(content=chatmessage ) )
                                    self.hashMessage[message.author.id]['content'] = ""
                                    self.hashMessage[message.author.id]['partNum'] = 0
                
                if self.hashMessage[message.author.id]['content'].strip() == "":
                    pass
                else:          
                    await message.channel.send(self.hashMessage[message.author.id]['content'])
                    chatmessage = str(self.hashMessage[message.author.id]['content']) .replace("<@" + str(message.author.id) + ">","")
                    self.hashMessage[message.author.id]['messages'].append(AIMessage(content=chatmessage ) )
                    self.hashMessage[message.author.id]['content'] = ""
                    self.hashMessage[message.author.id]['partNum'] = 0
                    

        await self.process_commands(message) # Important to allow commands to still function
    
    def setup_hook(self):
        self.logger.debug("Running")
        self.add_cog(CustomCommandCog(self,ollamaclient=self.ollamaclient,
                                      chat_ollama=self.chat_ollama,
                                      logger=self.logger,
                                      hashMessage=self.hashMessage))
        
    def get_bot_client(self):
        return self
    
    async def on_ready(self):
        self.logger.debug(f"Bot is ready. Logged in as {self.user}")