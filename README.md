# Da Chin Discord Bot

This is a Discord bot with various functions, primarily serving as a YouTube audio music bot in voice channels.

## Features

- **YouTube Music Playback**: Play music from YouTube in any voice channel in your Discord server.
- 

## Requirements

- **Python 3.10+**
- **Discord.py**: `pip install discord.py`
- **Other Dependencies**: Listed in `requirements.txt`

## Setup and Installation
### 1. Clone the Repository:
```bash
git clone https://github.com/DumplingCodeEater/Discord-Bot.git
cd Discord-Bot
```
### 2. Set Up Environment Variables:
- Option 1: Create a ```.env``` file in the root directory and add your discord bot token.
- Option 2: Add your discord bot token as a secret (if your server gives you an option to add secrets)

*Replace "your_discord_token" below with your actual discord bot token*
```env 
TOKEN = "your_discord_token"  
```
### 3. Run the Dockerfile:
```Dockerfile
docker build -t discord-bot .
docker run --env-file .env discord-bot
```
