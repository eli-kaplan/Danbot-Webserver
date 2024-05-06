from collections import defaultdict

import discord
from discord.ext import commands

import database
import db_entities
from utils import scapify, bingo
from utils.autocomplete import player_names, team_names, tile_names

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

        team_members = database.get_players_by_team_id(team.team_id)
        player_block = "```ansi\n"
        rank = 0
        for player in team_members:
            rank = rank + 1
            player = db_entities.Player(player)
            spaces_needed = 56 - len(f"Rank {rank}: {player.player_name[:40]}") - len(f"{player.tiles_completed} tiles ({scapify.int_to_gp(player.gp_gained)})")
            result = f"{ftext + fred}Rank {rank}:{fend} {player.player_name[:40]}{' ' * spaces_needed}{ftext + fblue}{player.tiles_completed} tiles {fend}{ftext + fgreen}({scapify.int_to_gp(player.gp_gained)})\n{fend}"
            if len(player_block) + len(result) > 1021:
                break
            player_block += result
        player_block += "```"

        embed.add_field(name="Players", value=player_block, inline=False)
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

    @discord.slash_command(name="progress", description="Check your progress on a specific tile")
    async def progress(self, ctx:discord.ApplicationContext,
                       team_name: discord.Option(str, "What is your team name?", autocomplete=discord.utils.basic_autocomplete(team_names)),
                       tile_name: discord.Option(str, "What tile are you checking?", autocomplete=discord.utils.basic_autocomplete(tile_names))):
        await ctx.defer()
        team = db_entities.Team(database.get_team_by_name(team_name))
        tile = db_entities.Tile(database.get_tile_by_name(tile_name))
        progress = bingo.check_progress(tile, team)
        if progress is None:
            ctx.respond(f"You have fully completed {tile.tile_name}!")
        else:
            ctx.respond(progress)

    @discord.slash_command(name="board", description="Get a list of tiles you've already completed")
    async def board(self, ctx:discord.ApplicationContext,
                    team_name: discord.Option(str, "What is your team name?", autocomplete=discord.utils.basic_autocomplete(team_names)),
                    board_type: discord.Option(str, "What kind of board would you like to see?", autocomplete=discord.utils.basic_autocomplete(["All Tiles","Completed Tiles","Incomplete Tiles", "Partial Tiles"]))):
        await ctx.defer()
        response = f"## {board_type} for {team_name}\n"
        team = db_entities.Team(database.get_team_by_name(team_name))
        tiles = database.get_tiles()
        completed_tiles = database.get_completed_tiles()
        complete_tile_dict = defaultdict(int)
        for tile in completed_tiles:
            tile = db_entities.Completed_Tile(tile)
            if tile.team_id == team.team_id:
                complete_tile_dict[tile.tile_id] = complete_tile_dict[tile.tile_id] + 1

        if board_type == "All Tiles":
            for tile in tiles:
                tile = db_entities.Tile(tile)
                if complete_tile_dict != 0:
                    response = response + f"{tile.tile_name}: "
                    for i in range(min(complete_tile_dict[tile.tile_id], tile.tile_repetition)):
                        response = response + ":white_check_mark:"
                    for i in range(0, tile.tile_repetition - complete_tile_dict[tile.tile_id]):
                        response = response + ":x:"
                    response = response + "\n"
        elif board_type == "Completed Tiles":
            for tile in tiles:
                tile = db_entities.Tile(tile)
                print(complete_tile_dict[tile.tile_id])
                if complete_tile_dict[tile.tile_id] > 0:
                    response = response + f"{tile.tile_name}: "
                    for i in range(min(complete_tile_dict[tile.tile_id], tile.tile_repetition)):
                        response = response + ":white_check_mark:"
                    for i in range(0, tile.tile_repetition - complete_tile_dict[tile.tile_id]):
                        response = response + ":x:"
        elif board_type == "Incomplete Tiles":
            for tile in tiles:
                tile = db_entities.Tile(tile)
                if complete_tile_dict[tile.tile_id] == 0:
                    response = response + f"{tile.tile_name}: "
                    for i in range(0, tile.tile_repetition - complete_tile_dict[tile.tile_id]):
                        response = response + ":x:"
        elif board_type == "Partial Tiles":
            for tile in tiles:
                tile = db_entities.Tile(tile)
                progress = bingo.check_progress(tile, team)
                if progress is not None:
                    response = response + progress + "\n"

        await ctx.respond(response)