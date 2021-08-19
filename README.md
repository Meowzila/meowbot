# meowbot
WIP discord bot written in python with various features like:


This bot loads all API keys and token from an external .env file.
You must create a file in the same directory as the bot.py file named .env.

FOR WEATHER TO WORK PROPERLY YOU MUST DOWNLOAD city.list.json.gz FROM https://bulk.openweathermap.org/sample/ AND EXTRACT TO THE BOT MAIN DIRECTORY
The bot uses this file to look up location id's using inputted city, state, country.

HOW TO RUN THIS BOT

  Download as zip and extract wherever or clone the project
  
  Install Python 3.9
  
  Install required libraries in requirements.txt with pip
    
  Use command python -m pip install -r requirements.txt in the project's main directory
 
 Create a file in the main directory called .env with the following information:
    
    # .env
    DISCORD_TOKEN=<Your Discord Bot Token Here>
    DISCORD_GUILD=<Your Discord Server Name Here>
    OPEN_WEATHER_API_KEY="<Your OpenWeather API Key Here>"
    STEAM_API_KEY=<Your Steam Web API Key Here>
  
  Copy the corresponding API keys and tokens in .env file
  
  Create a discord app and convert into User Bot
  
  Generate token and paste into .env file
  
  Enable Server Members Intent in bot tab
  
  Invite bot to server
  
  Run bot.py


Anything and Everything is subject to change and I will do my best to keep this README updated!
