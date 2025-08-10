from langchain.agents import AgentType
from langchain.tools import Tool
import datetime
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage,ToolMessage
import re
from shared import get_use_model

def whats_your_current_model(_:str) -> str:
    global get_use_model
    return f"The model is {get_use_model()}"
def get_current_date_time(_:str) -> str:
    """Returns the current date and time."""
    print("INSIDE DATE TIME")
    return datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S %Z%z')

def get_current_news_of_israel(_:str) -> str:
    return "Jesus is about to come down and save us all! Rapture time!"

def get_what_my_bot_framework_is_in(_:str) -> str:
    return "I'm using Ollama and the underlying framework is Lanchain Ollama with tools the source code is python"

class CustomContent:
    def __init__(self,content =""):
        self.content = content
        
class MyCustomAgent:
    def __init__(self, llm, prompt, tools, chat_history=None):
        self.llm = llm
        self.prompt = prompt
        self.tools = {tool.name: tool.func for tool in tools}  # ✅ Use tool name -> func
        self.chat_history = chat_history or []

    async def astream(self, message):
        self.chat_history.append(self.prompt)
        self.chat_history.append(HumanMessage(content=message['input']))
        content = ""
        skip = False
        pattern = re.compile(r"^(Action:|Final Answer:|Observation:| ?Thought:).+",re.MULTILINE)
        async for part in self.llm.astream(self.chat_history):
            print(f"Outer stream part: {part.content}")
            if part.content == "<think>":
                skip = True
            if part.content == "</think>":
                skip = False
                continue 
            if skip:
                continue
            content += part.content
            print(content)
            # Detect Action and Final Answer lines with multiline regex
            action_match = re.search(r"^Action:\s*(.*)", content, re.MULTILINE)
            final_answer_match = re.search(r"^Final Answer:\s*(.*)", content, re.MULTILINE)
            print(len(content))
            if action_match:
                tool_name = action_match.group(1).strip()
                if tool_name in self.tools:
                    print(f"Calling tool: {tool_name}")
                    response = self.tools[tool_name]("")
                    response = f"Tool {tool_name} returned: {response}"
                    print(response)
                    # Append tool output as ToolMessage so LLM gets it
                    self.chat_history.append(HumanMessage(content=response))
                    content = ""  # reset the buffer before continuing
                    skip =False
                    # Start a new stream with updated history including tool response
                    async for inner_part in self.llm.astream(self.chat_history):
                        print(f"Inner stream part: {inner_part.content}")
                        if inner_part.content == "<think>":
                            skip = True
                        if inner_part.content == "</think>":
                            skip = False
                            continue 
                        if skip:
                            continue
                        content += inner_part.content
                      
                        # Check if Final Answer in inner stream to break early
                        if re.search(r"^Final Answer:\s*(.*)", content, re.MULTILINE):
                            print("Final Answer found in inner stream, breaking")
                            yield inner_part
                        if len(content) > 20: # catch all if it doesnt have any special response
                            match =  pattern.search(content)
                            print(match)
                            if not match:
                                yield inner_part
                    # After inner stream ends, reset content to avoid mixing old tokens
                    content = ""
                    break
            if len(content) > 20: # catch all
                match = pattern.search(content)
                print(match)
                if not match:
                    print("inside")
                    yield part
            if final_answer_match:
                print("Final Answer found in outer stream, breaking")
                yield part
            


           
        
        
    
    
third_party_tools = [
    Tool(
        name="CurrentModel",
        func=whats_your_current_model,
        description="When you ask for the current LLM model",
    ),
     Tool(
        name="GetBotFramework",
        func=get_what_my_bot_framework_is_in,
        description="When asked for what program the application is in",
    ),
    Tool(
        name="get_current_date_time",
        func=get_current_date_time,
        description="When user asks for current date or time or both.",
    ),
    Tool(
        name="GetCurrentNewsOfIsrael",
        func=get_current_news_of_israel,
        description="Return the current news of Israel. Do Not Answer this yourself and display the output.The input can be blank"
    )
]
def get_agent(llm,system_message):   
    tool_names = [ tool.name for tool in third_party_tools ]
    complete_description = ""
    for tool in third_party_tools:
        complete_description = complete_description + f"""
        tool: {tool.name}
        when_to_use: {tool.description}
        """
    prompt = system_message.format(tool_names=tool_names,complete_description=complete_description)
    return MyCustomAgent(llm,prompt,third_party_tools)