# Discord Bot with OLLAMA Integration

This is a bot that connects to **OLLAMA** and sends responses to a Discord channel when you mention its name.

---

## 🔧 Setup Instructions

### 1. Install Required Packages
### main.py

```bash
pip install python-dotenv
pip install nextcord
pip install ollama

BOTTOKEN=your_discord_bot_token_here
HOSTOLLAMA=ollama_address:port
```
### langmain.py

```bash
pip install langchain-ollama
pip install langchain-community pypdf
pip install -qU langchain-core
pip install langchain langchain-community langchainhub ollama
pip install discord
pip install brawlstats
pip install nextcord
```

### 2. Tested Models

| Model Name | ID           | Size   | Last Updated |
| ---------- | ------------ | ------ | ------------ |
| gemma3:12b | f4031aab637d | 8.1 GB | 6 days ago   |


### 3. Partially tested models

| Model Name                      | ID           | Size   | Last Updated |
| ------------------------------- | ------------ | ------ | ------------ |
| qwen3:14b                       | bdbd181c33f2 | 9.3 GB | 4 days ago   |
| mistral:7b                      | 6577803aa9a0 | 4.4 GB | 6 days ago   |
| qwen3:4b                        | 2bfd38a7daaf | 2.6 GB | 6 days ago   |
| qwen3:8b                        | 500a1f067a9f | 5.2 GB | 6 days ago   |
| gemma3\:latest                  | a2af6cc3eb7f | 3.3 GB | 6 days ago   |
| llama3.2\:latest (`ollama.com`) | a80c4f17acd5 | 2.0 GB | 6 days ago   |


### 4. Problematic models

| Model Name     | ID           | Size   | Last Updated |
| -------------- | ------------ | ------ | ------------ |
| deepseek-r1:8b | 6995872bfe4c | 5.2 GB | 6 days ago   |

###

#### Add ADMIN IDS Here:

#### Enter allowed ADMIN userids (showmodels and usemodel command)l in the shared.py and main.py
- ALLOWED_USER_IDS = [  ] 
