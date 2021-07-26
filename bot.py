import os
import requests
import discord
from dotenv import load_dotenv
from discord.ext import commands
from pymongo import MongoClient

import pprint
pp = pprint.PrettyPrinter(indent=4)

# Set discord bot intents
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Load token and guild info from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
w_api_key = os.getenv('OPEN_WEATHER_API_KEY')
steam_key = os.getenv('STEAM_API_KEY')

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['user_database']


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds)
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    # Load basic member info
    new_members = 0
    async for member in guild.fetch_members():
        cursor = db['Users']
        if cursor.find_one({'id': member.id}):
            break
        else:
            cursor.insert_many([{'id': member.id, 'member_name': member.name, 'display_name': member.display_name}])
            new_members += 1
    print(f'{new_members} new members since last connection!')


@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')


@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


########################################################################################################################
# BASIC COMMANDS
########################################################################################################################

# List currently implemented features
@bot.command(name='features')
async def featurelist(ctx):
    response = 'Soon:tm:'
    await ctx.send(response)


# Tells bad jokes
@bot.command(name='dadjoke')
async def dadjoke(ctx):
    dad_joke = requests.get('https://icanhazdadjoke.com/slack')
    joke = dad_joke.json()
    await ctx.send(joke['attachments'][0]['text'])


# List basic user info
@bot.command(name='about')
async def about(ctx, *, user=None):
    cursor = db['Users']
    if user is None:
        result = cursor.find_one({'display_name': ctx.message.author.display_name})
        await ctx.send(f'ID: {result["id"]} \n'
                       f'Username: {result["member_name"]} \n'
                       f'Display Name: {result["display_name"]} \n')
    else:
        result = cursor.find_one({'display_name': user})
        if result is None:
            await ctx.send(f'User {user} not found!')
        else:
            await ctx.send(f'ID: {result["id"]} \n'
                           f'Username: {result["member_name"]} \n'
                           f'Display Name: {result["display_name"]}')


# Set user location for other features
@bot.command(name='set_location')
async def set_location(ctx, *, loc=None):
    cursor = db['Users']
    if loc is None:
        await ctx.send(f'Please enter a city location.')
    else:
        cursor.update_one({'id': ctx.message.author.id}, {'$set': {'location': loc}})
        await ctx.send(f'City set to {loc}!')


# Retrieve user location
@bot.command(name='location')
async def location(ctx):
    cursor = db['Users']
    result = cursor.find_one({'id': ctx.message.author.id})
    if result["location"] is None:
        await ctx.send(f'No location set, please use !set_location to set your location!')
    else:
        await ctx.send(f'{result["location"]}')


########################################################################################################################
# MISC
########################################################################################################################


# Error Logging WIP
@bot.event
async def on_error(event, *args):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise
    await event.send('Error')


bot.run(TOKEN)
