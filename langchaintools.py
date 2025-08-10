from langchain.agents import AgentType
from langchain.tools import Tool
import nextcord
import datetime
from langchain_core.messages import HumanMessage
import re
from langchain_ollama.chat_models import ChatOllama
from ollama import AsyncClient
import inspect
import brawlstats
import os
from typing import AsyncIterator, Iterator

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

use_model = "gemma3:12b"
def get_use_model():
    global use_model
    return use_model

def set_use_model(model):
    global use_model
    use_model = model
    

def create_ollamaclient (host = "None"):
    return AsyncClient(host=host)

def create_chat_ollama(base_url=None,model=None,temperature=None):
    return ChatOllama(
        base_url=base_url,
        model = model,
        temperature = temperature,
        streaming=True
        )

async def get_user_from_id(bot,_:str) -> str:
    try:
        user = await bot['bot'].fetch_user(int(_))
        content = f'User: {user.name}'
    except:
        content = "Sorry cannot find user"
    return content
        
async def get_message_history(bot,_:str) -> str:
    content = ""
    async for message in bot['message'].channel.history(limit=300):  # You can change limit or use before/after
        content = f"{content } {message.author.id}: {message.content}\n"
    return f"""This is the message history where format is author.id: message content 
              {content}"""

def brawl_stars_stats_for_tag(bot,_:str) -> str:
    content = "Sorry can't find user id"
    BRAWLTOKEN=os.environ.get("BRAWLAPI")
    brawlclient = brawlstats.Client(token=BRAWLTOKEN)
    if "#" in _[:2]:
        try:
            response_gotten = brawlclient.get_player(_)
        except:
            content = "sorry can't get response invalid tag"
        content = f"""
        Name: {response_gotten.name}
        Tag: {response_gotten.tag}
        Trophies: {response_gotten.trophies}
        Highest  Trophies: {response_gotten.highest_trophies}
        3v3 wins: {response_gotten.team_victories} Solo wins: {response_gotten.solo_victories}
        Club: {response_gotten.club.name}
        """
        if response_gotten.brawlers:
            top = response_gotten.brawlers[0]
            content = content + f"Best brawler: {top.name} Trophies {top.trophies}"
    else: 
        content = "invalid tag"
        
    return f'{content}'


def brawl_stars_ranking_for_countries(bot,_:str) -> str:
    def get_country(x):
        return {'canada':'CA',
                'united states': 'US',
                'england':'GB'}.get(x.lower(),"NotFound").upper()

    BRAWLTOKEN=os.environ.get("BRAWLAPI")
    country = get_country(_)
    if country == "NOTFOUND":
        content = "Sorry that country isn't found informed the developer"
    else:
        brawlclient = brawlstats.Client(token=BRAWLTOKEN)
        content = ""
        content_array = brawlclient.get_rankings(ranking="clubs",region=country,limit=15)
        for single in content_array:


            singleContent = f''' Tag: {single.tag}	
                            Name: {single.name}
                            Trophies: {single.trophies}
                            Rank: {single.rank}
                            MemberCount: {single.memberCount}
                            BadgeID: {single.badgeId}
                        '''
            content = content + singleContent
    return f'{content}'


def get_discord_server_members(bot,_:str) -> str:
    guild_members = [ member.name for member in bot['message'].guild.members  ]
    all_guild_members = " ".join(guild_members)
    return f'The list of members on this channel on server are {all_guild_members}'
    
def get_discord_online_server_members(bot,_:str) -> str:
    guild_members = [ member.name for member in bot['message'].guild.members if member.status != nextcord.Status.offline ]
    all_guild_members = " ".join(guild_members)
    return f'The list of members on this channel on server are {all_guild_members}'

def get_echo_with_inputs(bot,_:str) -> str:
    return f"echo {_}"
   
def whats_your_current_model(bot,_:str) -> str:
    global get_use_model
    return f"The model is {get_use_model()}"
def get_current_date_time(bot,_:str) -> str:
    """Returns the current date and time."""
    return datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S %Z%z')

def get_what_my_bot_framework_is_in(bot,_:str) -> str:
    return "I'm using Ollama and the underlying framework is Lanchain Ollama with tools the source code is python"

    
third_party_tools = [
     Tool(
        name='DiscordUserNameFromId-',
        func=get_user_from_id,
        description="Converts discord UserId to name using userid as input"
    ),
     Tool(
        name ="BrawlStarsRankingforCountries-",
        func=brawl_stars_ranking_for_countries,
        description="When the user asks to rank the brawl stars it takes the country name as input."
    ),
     Tool(
        name ="BrawlStarsPlayerRetrieval-",
        func=brawl_stars_stats_for_tag,
        description="When the user asks for info for a brawl stars player taking the tag starting with # as input."
    ),
     Tool(
        name ="Discord_Message_History-",
        func=get_message_history,
        description="Get this record when user asks about Message history and do what the user asks",
    ),
    Tool(
        name ="Discord_Server_Members-",
        func=get_discord_server_members,
        description="When the user asks for the list of server members",
    ),
        Tool(
        name ="Discord_Online_Server_Members-",
        func=get_discord_online_server_members,
        description="When the user asks for the list of members who are online",
    ),
    # Tool(
    #     name ="Echo",
    #     func=get_echo_with_inputs,
    #     description="When the user says echo, say arguments as input",
    # ),
     Tool(
        name ="CurrentModel-",
        func=whats_your_current_model,
        description="When you ask for the current LLM model",
    ),
    Tool(
         name ="GetBotFramework-",
        func=get_what_my_bot_framework_is_in,
        description="When asked for what program the application is in",
    ),
    Tool(
        name = "get_current_date_time-",
        func=get_current_date_time,
        description="When user asks for current date or time or both. it returns UTC date/time",
    )
]
   


class CustomContent:
    def __init__(self,content =""):
        self.content = content

class MyCustomToolEngine:
    def __init__(self, discord, tools,logger):
        self.discord = discord
        self.logger = logger
        self.tools = self.__parse_tools(tools)
        
    def __parse_tools(self,tools):
        tmp = {}
        for i in tools:
            tmp[i.name] = i
        return tmp
    def get_tools_keys(self):
        return self.tools.keys()
    def get_tools(self):
        return self.tools
    def run_tool(self,name,arguments=""):
        return self.tools[name].func(self.discord,arguments)
    def tool_inspect(self,name):
        return self.tools[name].func
        
class MyCustomAgent:
    def __init__(self, llm, prompt, tool_engine, logger, chat_history=None):
        self.llm = llm
        self.prompt = prompt
        self.logger = logger
        self.tool_engine = tool_engine  # ✅ Use tool name -> func
        self.chat_history = chat_history or []

    async def astream(self, message):
        self.chat_history.append(self.prompt)
        self.chat_history.append(HumanMessage(content=message['input']))
        match_no_action = True  #how to see if map for action was called
        skip = False
        content = ""
        pattern = re.compile(r"^(Action:|Final ?Answer:|Observation:|Action Input:| {0,2}Thought:).*",re.MULTILINE)
        async for part in self.llm.astream(self.chat_history):
            self.logger.debug(f"Outer stream part: {part.content}")
            if part.content == "<think>":
                skip = True
            if part.content == "</think>":
                skip = False
                continue 
            if skip:
                continue
            content += part.content
            self.logger.debug(content)
            self.logger.debug(len(content))

            # Detect Action and Final Answer lines with multiline regex
            action_match = re.search(r"^Action:\s*([a-zA-Z_]+[-])", content, re.MULTILINE)
            action_match_argument = re.search(r"^Action Input:\s*(.*)", content, re.MULTILINE)
            final_answer_match = re.search(r"^Final ?Answer:\s*(.*)", content, re.MULTILINE)
            if action_match:
                tool_argument = ""
                if action_match_argument:
                    tool_argument = action_match_argument.group(1).strip()

                tool_name = action_match.group(1).strip()
                if tool_name in self.tool_engine.get_tools_keys():
                    self.logger.debug(f"Calling tool: {tool_name}")
                    if inspect.iscoroutinefunction(self.tool_engine.tool_inspect(tool_name)):
                        response =  await self.tool_engine.run_tool(tool_name,tool_argument)
                    else:
                        response = self.tool_engine.run_tool(tool_name,tool_argument)
                        
                    response = f"Tool {tool_name} returned: {response}"
                    self.logger.debug(response)
                    # Append tool output as ToolMessage so LLM gets it
                    self.chat_history.append(HumanMessage(content=response))
                    self.logger.debug("Resetting content before async")
                    content = ""  # reset the buffer before continuing
                    skip =False
                    match_no_action_inner = True # Only share part if there is no Final Answer or any type of tagging
                    # Start a new stream with updated history including tool response
                    async for inner_part in self.llm.astream(self.chat_history):
                        self.logger.debug(f"Inner stream part: {inner_part.content}")
                        if inner_part.content == "<think>":
                            skip = True
                        if inner_part.content == "</think>":
                            skip = False
                            continue 
                        if skip:
                            continue
                        content += inner_part.content
                        self.logger.debug(content)
                        # Check if Final Answer in inner stream to break early
                        if re.search(r"^Final ?Answer:\s*(.*)", content, re.MULTILINE):
                            self.logger.debug("Final Answer found in inner stream, breaking")
                            yield inner_part
                        if ' ' in content.lstrip(): # catch all
                            match_no_action_inner = pattern.search(content)
                            if not match_no_action_inner:
                                if len(content.split(' ')) == 2 and ' ' in inner_part.content: #get left over buffer and make sure its not duplicate
                                    self.logger.debug(content)
                                    self.logger.debug(f'*{inner_part.content}*')
                                    yield CustomContent(content=content.split(' ')[0] + " " + inner_part.content)
                                else:
                                    self.logger.debug(f"*{inner_part.content}*")
                                    yield inner_part
                        
                    # After inner stream ends, reset content to avoid mixing old tokens
                    self.logger.debug("Resetting content")
                    content = ""
                    break
            if ' ' in content.lstrip(): # catch all
                match_no_action = pattern.search(content)
                self.logger.debug(match_no_action)

                if not match_no_action:
                    if len(content.split(' ')) == 2 and ' ' in part.content:
                        self.logger.debug(content)
                        self.logger.debug(f'*{part.content}*')
                        yield CustomContent(content=content.split(' ')[0] + " " + part.content)
                    else:
                        self.logger.debug(f"*{part.content}*")
                        yield part



            if final_answer_match:
                self.logger.debug("Final Answer found in outer stream, breaking")
                yield part
            


def get_agent(llm,system_message,bot,logger):   
    tool_names = [ tool.name for tool in third_party_tools ]
    complete_description = ""
    for tool in third_party_tools:
        complete_description = complete_description + f"""
        tool: {tool.name}
        when_to_use: {tool.description}
        """
    tool_engine = MyCustomToolEngine(bot,third_party_tools,logger)
    prompt = system_message.format(tool_names=tool_names,complete_description=complete_description)
    return MyCustomAgent(llm,prompt,tool_engine,logger)