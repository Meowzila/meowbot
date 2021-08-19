import requests
import discord
from discord.ext import commands
from pymongo import MongoClient
import datetime
import json
from bot import w_api_key

client = MongoClient('localhost', 27017)
db = client['user_database']

# OpenWeatherMap Information
base_url = "http://api.openweathermap.org/data/2.5/weather?"
icon_url = "https://openweathermap.org/img/wn/"


def f_to_c(f):
    c = (f - 32) / 1.8
    return c


def create_weather_embed(_city, _state, _country, _loc_id=None):
    combined_url = base_url + "appid=" + w_api_key + "&id=" + str(_loc_id) + "&units=imperial"
    weather_data = requests.get(combined_url).json()
    delta = datetime.timedelta(seconds=weather_data["timezone"])
    actual_time = datetime.datetime.utcfromtimestamp(weather_data["dt"]) + delta

    if _state is None:
        weather_embed = discord.Embed(
            title=f'Weather in {_city} at {actual_time.strftime("%I:%M %p")} ({_country})')
    else:
        weather_embed = discord.Embed(
            title=f'Weather in {_city}, {_state} at {actual_time.strftime("%I:%M %p")} ({_country})')
    weather_embed.set_thumbnail(url=icon_url + weather_data["weather"][0]["icon"] + "@2x.png")
    weather_embed.add_field(name="Current Conditions: ",
                            value=f'{weather_data["weather"][0]["description"]} at '
                                  f'{round(f_to_c(weather_data["main"]["temp"]))}°C / '
                                  f'{round((weather_data["main"]["temp"]))}°F')
    weather_embed.set_footer(text="Data provided by OpenWeatherMap")
    return weather_embed


class WeatherCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Weather command
    @commands.command(name='weather')
    async def weather(self, ctx, city=None, state=None, country=None, overflow=None):
        cursor = db['Users']
        result = cursor.find_one({'id': ctx.message.author.id})

        # No input, location loaded from db
        if city is None and state is None and country is None:
            city, state, country, loc_id = result["city"], result["state"], result["country"], result["location_id"]
            try:
                embed = create_weather_embed(city, state, country, loc_id)
                await ctx.send(embed=embed)
            except KeyError:
                await ctx.send(f'Please set your location using !set_location')

        # US city names with 2 words
        elif len(state) > 2 and overflow is not None:
            new_state = country
            new_country = overflow
            city += (" " + state)
            f = open('city.list.json', encoding='utf-8')
            data = json.load(f)
            try:
                for place in range(0, 8277210):
                    if data[place]["name"] == city and data[place]["state"] == new_state and data[place]["country"] == new_country:
                        loc_id = data[place]["id"]
                        embed = create_weather_embed(city, new_state, new_country, loc_id)
                        f.close()
                        await ctx.send(embed=embed)
                        break
            except IndexError:
                await ctx.send(f'Invalid OpenWeather Location!')

        # International locations with 2 words
        elif len(state) > 2 and overflow is None:
            city += (" " + state)
            f = open('city.list.json', encoding='utf-8')
            data = json.load(f)
            try:
                for place in range(0, 8277210):
                    if data[place]["name"] == city and data[place]["country"] == country:
                        loc_id = data[place]["id"]
                        embed = create_weather_embed(city, None, country, loc_id)
                        f.close()
                        await ctx.send(embed=embed)
                        break
            except IndexError:
                await ctx.send(f'Invalid OpenWeather Location!')

        # Everywhere else
        else:
            try:
                f = open('city.list.json', encoding='utf-8')
                data = json.load(f)
                # International locations
                if country is None:
                    country = state
                    try:
                        for place in range(0, 8277210):
                            if data[place]["name"] == city and data[place]["country"] == country:
                                loc_id = data[place]["id"]
                                embed = create_weather_embed(city, state, country, loc_id)
                                f.close()
                                await ctx.send(embed=embed)
                                break
                    except IndexError:
                        await ctx.send(f'Invalid OpenWeather Location!')
                # US locations
                else:
                    try:
                        for place in range(0, 8277210):
                            if data[place]["name"] == city and data[place]["state"] == state and data[place]["country"] == country:
                                loc_id = data[place]["id"]
                                embed = create_weather_embed(city, state, country, loc_id)
                                f.close()
                                await ctx.send(embed=embed)
                                break
                    except IndexError:
                        await ctx.send(f'Invalid OpenWeather Location!')
            except KeyError:
                await ctx.send(f'Please set your location using !set_location')

    # Set user location
    @commands.command(name='set_location')
    async def set_location(self, ctx, city=None, state=None, country=None):
        cursor = db['Users']
        f = open('city.list.json', encoding='utf-8')
        data = json.load(f)

        # US Location (city, state, country)
        if city is not None and state is not None and country is not None:
            try:
                for place in range(0, 8277210):
                    if data[place]["name"] == city and data[place]["state"] == state and data[place]["country"] == country:
                        location_id = data[place]["id"]
                        cursor.update_one({'id': ctx.message.author.id},
                                          {'$set': {'city': city,
                                                    'state': state,
                                                    'country': country,
                                                    'location_id': location_id}})
                        await ctx.send(f'Location successfully set to {city}, {state} ({country})!')
                        break
            except IndexError:
                await ctx.send(f'Invalid location!')

        # International Location (city, country)
        elif city is not None and state is not None and country is None:
            country = state
            try:
                for place in range(0, 8277210):
                    if data[place]["name"] == city and data[place]["country"] == country:
                        location_id = data[place]["id"]
                        cursor.update_one({'id': ctx.message.author.id},
                                          {'$set': {'city': city,
                                                    'state': None,
                                                    'country': country,
                                                    'location_id': location_id}})
                        await ctx.send(f'Location successfully set to {city}, {country}!')
                        break
            except IndexError:
                await ctx.send(f'Invalid location!')

        else:
            await ctx.send(f'Please use the following format:\n'
                           f'US: <city> <state code> <country code>\n'
                           f'ANYWHERE ELSE: <city> <country code>')

        f.close()

    # Retrieve user location
    @commands.command(name='location')
    async def location(self, ctx):
        cursor = db['Users']
        result = cursor.find_one({'id': ctx.message.author.id})
        try:
            if result["state"] is not None:
                await ctx.send(f'{result["city"]}, {result["state"]} {result["country"]}')
            else:
                await ctx.send(f'{result["city"]}, {result["country"]}')
        except KeyError:
            await ctx.send(f'No location set, please use !set_location to set your location!')


def setup(bot):
    bot.add_cog(WeatherCommands(bot))
