from shared import TOKEN
from discordbot import create_bot
from shared import create_chat_ollama
from shared import create_ollamaclient
from shared import logger
from shared import get_url_for_ollama
from langchaintools import get_use_model

def main():
    print("Running")
    bot = create_bot(create_ollamaclient(host=get_url_for_ollama()),create_chat_ollama(
                    base_url=get_url_for_ollama(),
                    model = get_use_model(),
                    temperature = 0.8
                ),logger)
    bot.setup_hook()
    bot.run(TOKEN)
    
if __name__ == "__main__":
    main()