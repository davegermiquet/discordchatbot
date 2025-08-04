from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import datetime

def get_current_datetime(_: str) -> str:
    """Returns the current date and time."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  
third_party_tools = [
    Tool(
        name="GetCurrentDateTime",
        func=get_current_datetime,
        description="Returns the current date and time. Input is ignored.",
    )
]
def get_agent(llm):
    agent = initialize_agent(
    tools=third_party_tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True)
    return agent