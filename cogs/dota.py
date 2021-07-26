import requests
import discord
from discord.ext import commands
from pymongo import MongoClient
import time

client = MongoClient('localhost', 27017)
db = client['user_database']

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
rk = 'https://dota2freaks.com/wp-content/uploads/sites/10/2020/02/dota-2-rank-'
dota_ranks_icons = {
    'Immortal': rk + 'immortal-placed.png',
    'Divine[5]': rk + 'divine-5.png', 'Divine[4]': rk + 'divine-4.png', 'Divine[3]': rk + 'divine-3.png', 'Divine[2]': rk + 'divine-2.png', 'Divine[1]': rk + 'divine-1.png',
    'Ancient[5]': rk + 'ancient-5.png', 'Ancient[4]': rk + 'ancient-4.png', 'Ancient[3]': rk + 'ancient-3.png', 'Ancient[2]': rk + 'ancient-2.png', 'Ancient[1]': rk + 'ancient-1.png',
    'Legend[5]': rk + 'legend-5.png', 'Legend[4]': rk + 'legend-4.png', 'Legend[3]': rk + 'legend-3.png', 'Legend[2]': rk + 'legend-2.png', 'Legend[1]': rk + 'legend-1.png',
    'Archon[5]': rk + 'archon-5.png', 'Archon[4]': rk + 'archon-4.png', 'Archon[3]': rk + 'archon-3.png', 'Archon[2]': rk + 'archon-2.png', 'Archon[1]': rk + 'archon-1.png',
    'Crusader[5]': rk + 'crusader-5.png', 'Crusader[4]': rk + 'crusader-4.png', 'Crusader[3]': rk + 'crusader-3.png', 'Crusader[2]': rk + 'crusader-2.png', 'Crusader[1]': rk + 'crusader-1.png',
    'Guardian[5]': rk + 'guardian-5.png', 'Guardian[4]': rk + 'guardian-4.png', 'Guardian[3]': rk + 'guardian-3.png', 'Guardian[2]': rk + 'guardian-2.png', 'Guardian[1]': rk + 'guardian-1.png',
    'Herald[5]': rk + 'herold-5.png', 'Herald[4]': rk + 'herold-4.png', 'Herald[3]': rk + 'herold-3.png', 'Herald[2]': rk + 'herold-2.png', 'Herald[1]': rk + 'herald1.png',
    'Unranked': 'https://cdn.discordapp.com/emojis/802039609168101417.png'}


def stats_embed(id_32, msg_auth, wins, total, draws, losses):
    try:
        r = requests.get(open_dota_url + 'players/' + id_32)
        dota = r.json()
        dota_embed = discord.Embed()
        dota_embed.set_author(name=msg_auth)
        dota_embed.set_thumbnail(url=dota_ranks_icons[dota_ranks[dota["rank_tier"]]])
        dota_embed.add_field(name="Lane Breakdown: ",
                             value=f'Wins: {wins}/{total}\n'
                                   f'Draws: {draws}/{total}\n'
                                   f'Losses: {losses}/{total}\n')
        dota_embed.add_field(name="Ranking: ",
                             value=f'{dota_ranks[dota["rank_tier"]]}')
        dota_embed.set_footer(text="Data provided by OpenDota")
        error = None
        return dota_embed, error
    except KeyError:
        error = 'Not all recent matches have been parsed by OpenDota, please try again later'
        return error


def lane_breakdown(steam32_id):
    match_id_req = requests.get(open_dota_url + 'players/' + steam32_id + '/recentMatches')
    match = match_id_req.json()
    n, parse_successes, wins, draws, losses = 0, 0, 0, 0, 0
    for recent_game in range(20):
        match_id_str = str(match[n]["match_id"])
        requests.get(open_dota_url + 'request/' + match_id_str)
        print(f'Parsing match_id: {match_id_str}')
        friendly_gold = friendly_lane_gold(match_id_str, steam32_id)
        enemy_gold = enemy_lane_gold(match_id_str, steam32_id)
        print(f'Friendly Gold: {friendly_gold}')
        print(f'Enemy Gold: {enemy_gold}\n')
        if friendly_gold is None:
            parse_successes -= 1
        elif friendly_gold > enemy_gold+500:
            wins += 1
        elif friendly_gold < enemy_gold-500:
            losses += 1
        else:
            draws += 1
        n += 1
        parse_successes += 1
    print(f'Wins: {wins}')
    print(f'Wins: {draws}')
    print(f'Wins: {losses}')
    print(f'Successfully parsed matches: {parse_successes}/20')
    return parse_successes, wins, draws, losses


def user_info(match_id, player_id):
    match_stats = requests.get(open_dota_url + 'matches/' + match_id).json()
    time.sleep(1.5)
    for player in range(0, 10):
        if match_stats["players"][player]["account_id"] == int(player_id):
            user = match_stats["players"][player]
            user_team = user["isRadiant"]
            user_lane = user["lane"]
            user_lane_role = user["lane_role"]
            user_worth = user["gold_t"][10]
            return user_team, user_lane, user_lane_role, user_worth


def friendly_lane_gold(match_id, player_id):
    match_stats = requests.get(open_dota_url + 'matches/' + match_id).json()
    user_team, user_lane, user_lane_role, user_worth = user_info(match_id, player_id)
    # Check if user is mid
    if user_lane and user_lane_role == 2:
        return user_worth
    for other_player in range(0, 10):
        other = match_stats["players"][other_player]
        try:
            if other["account_id"] != int(player_id) and other["isRadiant"] is user_team and other["lane"] == user_lane:
                return other["gold_t"][10] + user_worth
        except KeyError:
            print(f'Unable to parse: {match_id}')


def enemy_lane_gold(match_id, player_id):
    match_stats = requests.get(open_dota_url + 'matches/' + match_id).json()
    user_team, user_lane, user_lane_role, user_worth = user_info(match_id, player_id)
    enemy_gold = 0
    for other_player in range(0, 10):
        other = match_stats["players"][other_player]
        try:
            if other["isRadiant"] != user_team and other["lane"] == user_lane and other["is_roaming"] is False:
                enemy_gold += other["gold_t"][10]
        except KeyError:
            print(f'Unable to parse: {match_id}')
    return enemy_gold


class DotaCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Sets steam32 and steam64 ids
    @commands.command(name='set_steam_ids')
    async def set_steam_ids(self, ctx, steam_id32=None, steam_id64=None):
        cursor = db['Users']
        try:
            if len(steam_id32) != 8 and len(steam_id64) != 17:
                await ctx.send(f'Invalid IDs. Please use format: !set_steam_ids steam32 steam64')
            elif steam_id32 is None or steam_id64 is None:
                await ctx.send(f'Invalid entry. Please use format: !set_steam_ids steam32 steam64')
            else:
                cursor.update_one({'id': ctx.message.author.id},
                                  {'$set': {'steam32': steam_id32, 'steam64': steam_id64}})
                await ctx.send(f'IDs set successfully!')
        except Exception:
            await ctx.send(f'You can find your steam32 and steam64 IDs at https://steamid.xyz')

    # Lists John's MMR
    @commands.command(name='john_stats')
    async def john_stats(self, ctx):
        john_id = '73578390'
        total, wins, draws, losses = lane_breakdown(john_id)
        dota_embed, error = stats_embed(john_id, 'Please Kill Me', wins, total, draws, losses)
        if error is None:
            await ctx.send(embed=dota_embed)
        else:
            await ctx.send(error)

    # Dota2 Stats
    @commands.command(name='stats')
    async def stats(self, ctx, *, other_user=None):
        cursor = db['Users']
        if other_user is None:
            result = cursor.find_one({'id': ctx.message.author.id})
            if result["steam32"] is None:
                await ctx.send(f'No Steam32 found, please enter your Steam32 and Steam64 IDs using !set_steam_ids')
            else:
                total, wins, draws, losses = lane_breakdown(result["steam32"])
                dota_embed, error = stats_embed(result["steam32"], ctx.message.author.display_name, wins, total, draws, losses)
                if error is None:
                    await ctx.send(embed=dota_embed)
                else:
                    await ctx.send(error)
        else:
            result = cursor.find_one({'display_name': other_user})
            total, wins, draws, losses = lane_breakdown(result["steam32"])
            dota_embed, error = stats_embed(result["steam32"], other_user, wins, total, draws, losses)
            if error is None:
                await ctx.send(embed=dota_embed)
            else:
                await ctx.send(error)


def setup(bot):
    bot.add_cog(DotaCommands(bot))

