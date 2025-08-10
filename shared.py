import logging
import sys
import os
from langchaintools import create_chat_ollama
from langchaintools import create_ollamaclient
from langchaintools import get_use_model
from dotenv import load_dotenv

load_dotenv()

POST_TYPE = "Character"
MAX_LENGTH = 1500
TOKEN=os.environ.get("BOTTOKEN")


logging.basicConfig(
    level=logging.DEBUG,  # Or use INFO in production
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('nextcord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler(sys.stdout))

#Enter allowed ADMIN userids (showmodels and usemodel command)
ALLOWED_USER_IDS = [  ] 

def get_hashMessage():
    global hashMessage
    return hashMessage


def get_chat_ollama():
    global chat_ollama
    return chat_ollama

def get_ollamaclient():
    global ollamaclient
    return ollamaclient

def get_url_for_ollama():
    return 'http://' + os.environ.get("HOSTOLLAMA")

chat_ollama = create_chat_ollama( base_url=get_url_for_ollama(),
                model = get_use_model(),
                temperature = 1.2)

ollamaclient = create_ollamaclient(get_url_for_ollama())
