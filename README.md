This is a bot that connects to OLLAMA and sends it to the discord channel when you mention its name
 
To get this running install the following:

pip install python-dotenv
pip install nextcord
pip install ollama

and setup the .env file:

BOTTOKEN= (bittoken)
HOSTOLLAMA=(ollama address:port)

For langmain.py you need:

pip install langchain-ollama
pip install langchain-community pypdf
pip install -qU langchain-core
pip install langchain langchain-community langchainhub ollama
pip install discord
pip install brawlstats

Models i've tried work for langmain.py:
gemma3:12b                            f4031aab637d    8.1 GB    6 days ago    

Some tested a bit:
qwen3:14b                             bdbd181c33f2    9.3 GB    4 days ago    
mistral:7b                            6577803aa9a0    4.4 GB    6 days ago    
qwen3:4b                              2bfd38a7daaf    2.6 GB    6 days ago    
qwen3:8b                              500a1f067a9f    5.2 GB    6 days ago    
gemma3:latest                         a2af6cc3eb7f    3.3 GB    6 days ago    
ollama.com/library/llama3.2:latest    a80c4f17acd5    2.0 GB    6 days ago  


inconsistnetly works here:

deepseek-r1:8b                        6995872bfe4c    5.2 GB    6 days ago    




