import discord
from discord.ext import commands

import database
import db_entities
from utils import scapify
from utils.autocomplete import player_names, team_names

ftext = "\u001b["

fnormal = "0;"
fbolt = "1;"
funderline = "4;"

fred = "31m"
fgreen = "32m"
fyellow = "33m"
fblue = "34m"
fwhite = "37m"
fend = ftext + "0m"

class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="help", description="A list of all my cool commands!")
    async def help(self, ctx: discord.ApplicationContext):
        await ctx.respond("I'm currently being updated. Most of my functionality isn't ready at the moment.")

    @discord.slash_command(name="team", description="Get a bunch of data about a team in the bingo")
    async def team(self, ctx: discord.ApplicationContext,
                   team_name: discord.Option(str, "What is the team name?", autocomplete=discord.utils.basic_autocomplete(team_names))):
        await ctx.defer()
        team = database.get_team_by_name(team_name)
        team = db_entities.Team(team)

        embed = discord.Embed(
            title = team.team_name,
            description="Here's some information about your team performance",
            color=discord.Colour.yellow()
        )

        total_gold = 0
        drop_dict = {}
        drops = database.get_drops_by_team_id(team.team_id)
        for drop in drops:
            drop = db_entities.Drop(drop)
            total_gold = drop.drop_quantity * drop.drop_value + total_gold
            drop_dict[drop.drop_name] = (drop.drop_quantity, drop.drop_value * drop.drop_quantity)


        embed.add_field(name="Points", value=team.team_points, inline=True)
        embed.add_field(name="Gold Gained", value=total_gold, inline=True) # Todo get gold
        embed.add_field(name="Total deaths", value=0, inline=True) # Todo get deaths

        drop_block = "```ansi\n"
        drop_dict = sorted(drop_dict.items(),key=lambda item: item[1][1], reverse=True)

        for key, value in drop_dict:
            spaces_needed = 56 - len(f"{value[0]} x {key}({scapify.int_to_gp(value[1])})")
            result = f"{ftext +fred}{value[0]} x{fend} {key}{' ' * spaces_needed}{ftext + fgreen}({scapify.int_to_gp(value[1])}){fend}\n"
            if len(drop_block) + len(result) > 1021:
                break
            drop_block += result
        drop_block += "```"

        kills = database.get_killcount_by_team_id(team.team_id)
        kill_dict = {}
        for kill in kills:
            kill = db_entities.Killcount(kill)
            kill_dict[kill.boss_name] = kill.kills

        kill_block = "```ansi\n"
        kill_dict = sorted(kill_dict.items(), key=lambda item: item[1], reverse=True)
        for key, value in kill_dict:
            spaces_needed = 56 - len(f"{key}{value}")
            result = f"{ftext + fred}{key}{fend}{' ' * spaces_needed}{ftext + fblue}{value}\n{fend}"
            if len(kill_block) + len(result) > 1021:
                break
            kill_block += result
        kill_block += "```"

        embed.add_field(name="Drops", value=drop_block, inline=False)
        embed.add_field(name="Kills", value=kill_block, inline=False)
        await ctx.respond(embed=embed)

    @discord.slash_command(name="player", description="Get a bunch of data about a player in the bingo")
    async def player(self, ctx: discord.ApplicationContext,
                     player_name: discord.Option(str, "What is the username?", autocomplete=discord.utils.basic_autocomplete(player_names))):
        await ctx.defer()
        player = database.get_player_by_name(player_name)
        player = db_entities.Player(player)

        embed = discord.Embed(
            title = player.player_name,
            description="Here's some information about your performance",
            color=discord.Colour.yellow()
        )

        embed.add_field(name="Tile contributions", value=f"{round(player.tiles_completed, 2)}", inline=True)
        embed.add_field(name="Gold gained", value=f"{scapify.int_to_gp(player.gp_gained)}", inline=True)
        embed.add_field(name="Total deaths", value=f"{player.deaths}", inline=True)

        drops = database.get_drops_by_player_id(player.player_id)

        drop_dict = {}
        for drop in drops:
            drop = db_entities.Drop(drop)
            drop_dict[drop.drop_name] = (drop.drop_quantity, drop.drop_value * drop.drop_quantity)

        drop_block = "```ansi\n"
        drop_dict = sorted(drop_dict.items(),key=lambda item: item[1][1], reverse=True)

        for key, value in drop_dict:
            spaces_needed = 56 - len(f"{value[0]} x {key}({scapify.int_to_gp(value[1])})")
            result = f"{ftext +fred}{value[0]} x{fend} {key}{' ' * spaces_needed}{ftext + fgreen}({scapify.int_to_gp(value[1])}){fend}\n"
            if len(drop_block) + len(result) > 1021:
                break
            drop_block += result
        drop_block += "```"

        kills = database.get_killcount_by_player_id(player.player_id)
        kill_dict = {}
        for kill in kills:
            kill = db_entities.Killcount(kill)
            kill_dict[kill.boss_name] = kill.kills

        kill_block = "```ansi\n"
        kill_dict = sorted(kill_dict.items(), key=lambda item: item[1], reverse=True)
        for key, value in kill_dict:
            spaces_needed = 56 - len(f"{key}{value}")
            result = f"{ftext + fred}{key}{fend}{' ' * spaces_needed}{ftext + fblue}{value}\n{fend}"
            if len(kill_block) + len(result) > 1021:
                break
            kill_block += result
        kill_block += "```"

        embed.add_field(name="Drops", value=drop_block, inline=False)
        embed.add_field(name="Kills", value=kill_block, inline=False)
        await ctx.respond(embed=embed)