import os
import requests
import discord
import time
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
GUILD = os.getenv('DISCORD_GUILD')
w_api_key = os.getenv('OPEN_WEATHER_API_KEY')
steam_key = os.getenv('STEAM_API_KEY')

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['user_database']


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
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


########################################################################################################################
# DOTA 2 COMMANDS
########################################################################################################################

# Various url bits
steam_api_url = 'api.steampowered.com/'
open_dota_url = 'https://api.opendota.com/api/'

dota_ranks = {
    8: 'Immortal',
    75: 'Divine[5]', 74: 'Divine[4]', 73: 'Divine[3]', 72: 'Divine[2]', 71: 'Divine[1]',
    65: 'Ancient[5]', 64: 'Ancient[4]', 63: 'Ancient[3]', 62: 'Ancient[2]', 61: 'Ancient[1]',
    55: 'Legend[5]', 54: 'Legend[4]', 53: 'Legend[3]', 52: 'Legend[2]', 51: 'Legend[1]',
    45: 'Archon[5]', 44: 'Archon[4]', 43: 'Archon[3]', 42: 'Archon[2]', 41: 'Archon[1]',
    35: 'Crusader[5]', 34: 'Crusader[4]', 33: 'Crusader[3]', 32: 'Crusader[2]', 31: 'Crusader[1]',
    25: 'Guardian[5]', 24: 'Guardian[4]', 23: 'Guardian[3]', 22: 'Guardian[2]', 21: 'Guardian[1]',
    15: 'Herald[5]', 14: 'Herald[4]', 13: 'Herald[3]', 12: 'Herald[2]', 11: 'Herald[1]',
    None: 'Unranked'}

# This is awful
rank_url = 'https://dota2freaks.com/wp-content/uploads/sites/10/2020/02/dota-2-rank-'
dota_ranks_icons = {
    'Immortal': rank_url + 'immortal-placed.png',
    'Divine[5]': rank_url + 'divine-5.png', 'Divine[4]': rank_url + 'divine-4.png', 'Divine[3]': rank_url + 'divine-3.png', 'Divine[2]': rank_url + 'divine-2.png', 'Divine[1]': rank_url + 'divine-1.png',
    'Ancient[5]': rank_url + 'ancient-5.png', 'Ancient[4]': rank_url + 'ancient-4.png', 'Ancient[3]': rank_url + 'ancient-3.png', 'Ancient[2]': rank_url + 'ancient-2.png', 'Ancient[1]': rank_url + 'ancient-1.png',
    'Legend[5]': rank_url + 'legend-5.png', 'Legend[4]': rank_url + 'legend-4.png', 'Legend[3]': rank_url + 'legend-3.png', 'Legend[2]': rank_url + 'legend-2.png', 'Legend[1]': rank_url + 'legend-1.png',
    'Archon[5]': rank_url + 'archon-5.png', 'Archon[4]': rank_url + 'archon-4.png', 'Archon[3]': rank_url + 'archon-3.png', 'Archon[2]': rank_url + 'archon-2.png', 'Archon[1]': rank_url + 'archon-1.png',
    'Crusader[5]': rank_url + 'crusader-5.png', 'Crusader[4]': rank_url + 'crusader-4.png', 'Crusader[3]': rank_url + 'crusader-3.png', 'Crusader[2]': rank_url + 'crusader-2.png', 'Crusader[1]': rank_url + 'crusader-1.png',
    'Guardian[5]': rank_url + 'guardian-5.png', 'Guardian[4]': rank_url + 'guardian-4.png', 'Guardian[3]': rank_url + 'guardian-3.png', 'Guardian[2]': rank_url + 'guardian-2.png', 'Guardian[1]': rank_url + 'guardian-1.png',
    'Herald[5]': rank_url + 'herold-5.png', 'Herald[4]': rank_url + 'herold-4.png', 'Herald[3]': rank_url + 'herold-3.png', 'Herald[2]': rank_url + 'herold-2.png', 'Herald[1]': rank_url + 'herald1.png',
    'Unranked': 'https://cdn.discordapp.com/emojis/802039609168101417.png'}


# Sets steam32 and steam64 ids
@bot.command(name='set_steam_ids')
async def set_steam_ids(ctx, steam_id32=None, steam_id64=None):
    cursor = db['Users']
    try:
        if len(steam_id32) != 8 and len(steam_id64) != 17:
            await ctx.send(f'Invalid IDs. Please use format: !set_steam_ids steam32 steam64')
        elif steam_id32 is None or steam_id64 is None:
            await ctx.send(f'Invalid entry. Please use format: !set_steam_ids steam32 steam64')
        else:
            cursor.update_one({'id': ctx.message.author.id}, {'$set': {'steam32': steam_id32, 'steam64': steam_id64}})
            await ctx.send(f'IDs set successfully!')
    except Exception:
        await ctx.send(f'You can find your steam32 and steam64 IDs at https://steamid.xyz')


# Lists John's MMR
@bot.command(name='john_mmr')
async def john_mmr(ctx):
    r = requests.get('https://api.opendota.com/api/players/73578390')
    dota = r.json()
    await ctx.send(f'Estimated MMR: {dota["mmr_estimate"]["estimate"]}\nRanked Tier: {dota_ranks[dota["rank_tier"]]}')


# Dota2 Stats
@bot.command(name='stats')
async def stats(ctx, *, other_user=None):
    cursor = db['Users']
    if other_user is None:
        result = cursor.find_one({'id': ctx.message.author.id})
        if result["steam32"] is None:
            await ctx.send(f'No Steam32 found, please enter your Steam32 and Steam64 IDs using !set_steam_ids')
        else:
            total, wins = lane_breakdown(result["steam32"])
            try:
                r = requests.get(open_dota_url + 'players/' + result["steam32"])
                dota = r.json()
                dota_embed = discord.Embed()
                dota_embed.set_author(name=ctx.message.author.display_name)
                dota_embed.set_thumbnail(url=dota_ranks_icons[dota_ranks[dota["rank_tier"]]])
                dota_embed.add_field(name="Lane Breakdown: ",
                                     value=f'Won their lane in {wins}/{total} games')
                dota_embed.add_field(name="Ranking: ",
                                     value=f'{dota_ranks[dota["rank_tier"]]}')
                dota_embed.set_footer(text="Data provided by OpenDota")
                await ctx.send(embed=dota_embed)
            except KeyError:
                await ctx.send(f'Not all recent matches have been parsed by OpenDota, please try again later')
    else:
        result = cursor.find_one({'display_name': other_user})
        try:
            total, wins = lane_breakdown(result["steam32"])
            r = requests.get(open_dota_url + 'players/' + result["steam32"])
            dota = r.json()
            dota_embed = discord.Embed()
            dota_embed.set_author(name=other_user)
            dota_embed.set_thumbnail(url=dota_ranks_icons[dota_ranks[dota["rank_tier"]]])
            dota_embed.add_field(name="Lane Breakdown: ",
                                 value=f'Their lane won in {wins}/{total} games')
            dota_embed.add_field(name="Ranking: ",
                                 value=f'{dota_ranks[dota["rank_tier"]]}')
            dota_embed.set_footer(text="Data provided by OpenDota")
            await ctx.send(embed=dota_embed)
        except KeyError:
            await ctx.send(f'Not all recent matches have been parsed by OpenDota, please try again later')


def lane_breakdown(steam32_id):
    match_id_req = requests.get(open_dota_url + 'players/' + steam32_id + '/recentMatches')
    match = match_id_req.json()
    n, parse_successes, wins = 0, 0, 0
    for recent_game in range(0, 20, 1):
        match_id_str = str(match[n]["match_id"])
        match_stats_req = requests.get(open_dota_url + 'matches/' + match_id_str)
        match_stats = match_stats_req.json()
        requests.get(open_dota_url + 'request/' + match_id_str)
        print(f'Parsing match_id: {match_id_str}\n')
        friendly_gold = 0
        enemy_gold = 0
        for player in range(0, 10, 1):
            if match_stats["players"][player]["account_id"] == int(steam32_id):
                for opposing_player in range(0, match_stats["human_players"]):
                    try:
                        if match_stats["players"][player]["lane_role"] == match_stats["players"][opposing_player]["lane_role"]\
                                and match_stats["players"][player]["account_id"] != match_stats["players"][opposing_player]["account_id"]:
                            if match_stats["players"][player]["isRadiant"] != match_stats["players"][opposing_player]["isRadiant"]:
                                enemy_gold += match_stats["players"][opposing_player]["gold_t"][10]
                            else:
                                friendly_gold += match_stats["players"][opposing_player]["gold_t"][10]
                                friendly_gold += match_stats["players"][player]["gold_t"][10]
                    except KeyError:
                        print(f'Unable to parse: {match_id_str}\n')
                try:
                    if match_stats["players"][player]["lane_role"] == 2:
                        friendly_gold += match_stats["players"][player]["gold_t"][10]
                    parse_successes += 1
                except KeyError:
                    print(f'Unable to parse: {match_id_str}\n')
        if friendly_gold > enemy_gold:
            wins += 1
        n += 1
    print(f'Wins: {wins}')
    print(f'Successfully parsed matches: {parse_successes}/20')
    return [parse_successes, wins]


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


# Pings bot
@bot.command(name='pingle')
async def pingle(ctx):
    await ctx.send(f'pongle {round(bot.latency * 1000)}ms')


########################################################################################################################
# WEATHER COMMANDS
########################################################################################################################

# OpenWeatherMap Information
base_url = "http://api.openweathermap.org/data/2.5/weather?"


# Weather command
@bot.command(name='weather')
async def weather(ctx, *, city=None):
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
