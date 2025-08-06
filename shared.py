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


logger = logging.getLogger('nextcord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler(sys.stdout))

def getLogger():
    return logger

ALLOWED_USER_IDS = [ 1307829880540364844,1216173756423077988 ] 







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
