# meowbot
My first Discord chat bot written in Python to practice calling JSON data from external APIs and store data in database


This bot loads all API keys and token from an external .env file.
You must create a file in the same directory as the bot.py file named .env.

Create a file in the main directory called .env with the following information:
    
    # .env
    DISCORD_TOKEN=<Your Discord Bot Token Here>
    DISCORD_GUILD=<Your Discord Server Name Here>
    OPEN_WEATHER_API_KEY="<Your OpenWeather API Key Here>"
    STEAM_API_KEY=<Your Steam Web API Key Here>
  
You can install the required libraries in requirements.txt with: python -m pip install -r requirements.txt

Some Features:
- Save user info such as location for other commands like !weather

![alt text](https://i.imgur.com/KsnNCyU.png)

- Can display weather information for most locations around the world

![alt text](https://i.imgur.com/HFjffhN.png)

- Parses opendota.com API for recent DOTA 2 games and calculates basic stats such as whether you "won" your lane or not based on the amount of gold you had at 10 minutes
- Ex 1. You have net worth of 5k as Pos 2 while the enemy Pos 2 has 6k: you've lost the lane
- Ex 2. You are laning Pos 1/5 against enemy Pos 3/4 and your lane has 7k gold while the enemy lane has 6k gold: you've won the lane
- Ex 3. Your net worth is within ~500 gold of the enemy net worth: your lane is a draw

![alt text](https://i.imgur.com/s5EGm8n.png)
