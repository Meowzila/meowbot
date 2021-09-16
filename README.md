# meowbot
WIP discord bot written in Python


This bot loads all API keys and token from an external .env file.
You must create a file in the same directory as the bot.py file named .env.

Create a file in the main directory called .env with the following information:
    
    # .env
    DISCORD_TOKEN=<Your Discord Bot Token Here>
    DISCORD_GUILD=<Your Discord Server Name Here>
    OPEN_WEATHER_API_KEY="<Your OpenWeather API Key Here>"
    STEAM_API_KEY=<Your Steam Web API Key Here>
  
You can install the required libraries in requirements.txt with: python -m pip install -r requirements.txt
