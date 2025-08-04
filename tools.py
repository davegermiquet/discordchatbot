from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import datetime

def get_current_datetime(_: str) -> str:
    """Returns the current date and time."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_current_news_of_israel(_:str) -> str:
    return "Jesus is about to come down and save us all! Rapture time!"

def get_what_my_bot_framework_is_in(_:str) -> str:
    return "I'm using Ollama and the underlying framework is Lanchain Ollama with tools the source code is python"

third_party_tools = [
     Tool(
        name="GetBotFramework",
        func=get_what_my_bot_framework_is_in,
        description="Always use this tool to answer the question whats the bot programmed in or framework used. Do not answer this yoursellf. The input is ignored",
    ),
    Tool(
        name="GetCurrentDateTime",
        func=get_current_datetime,
        description="Returns the current date and time. Input is ignored.",
    ),
    Tool(
        name="GetCurrentNewsOfIsrael",
        func=get_current_news_of_israel,
        description="Always use this tool to answer the question whats the current news of Israel. Do Not Answer this yourself and display the output.The input can be blank"
    )
]
def get_agent(llm):
    agent = initialize_agent(
    tools=third_party_tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True)
    return agent