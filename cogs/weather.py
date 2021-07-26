import requests
import discord
from discord.ext import commands
from pymongo import MongoClient
import time
from bot import w_api_key

client = MongoClient('localhost', 27017)
db = client['user_database']

# OpenWeatherMap Information
base_url = "http://api.openweathermap.org/data/2.5/weather?"


class WeatherCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Weather command
    @commands.command(name='weather')
    async def weather(self, ctx, *, city=None):
        cursor = db['Users']

        def f_to_c(f):
            c = (f - 32) / 1.8
            return c

        result = cursor.find_one({'id': ctx.message.author.id})
        if city is None and result["location"] is None:
            await ctx.send(f'Please set your location using !set_location')
        if city is None and result["location"] is not None:
            city = result["location"]
        combined_url = base_url + "appid=" + w_api_key + "&q=" + city + "&units=imperial"
        weather_data = requests.get(combined_url).json()
        weather_embed = discord.Embed(
            title=f'Weather in {city} at {time.strftime("%I:%M %p")}')

        try:
            weather_embed.add_field(name="Current Conditions: ",
                                    value=f'{weather_data["weather"][0]["description"]} at '
                                          f'{round(f_to_c(weather_data["main"]["temp"]))}°C / '
                                          f'{round((weather_data["main"]["temp"]))}°F')
            weather_embed.set_footer(text="Data provided by OpenWeatherMap")
            await ctx.send(embed=weather_embed)
        except Exception:
            await ctx.send(f'{city} is not a valid city name.')


def setup(bot):
    bot.add_cog(WeatherCommands(bot))
