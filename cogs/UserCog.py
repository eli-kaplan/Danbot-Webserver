import os
import urllib
from collections import defaultdict

import discord
from discord.ext import commands

from utils import bingo, database, db_entities
from utils.autocomplete import player_names, team_names, tile_names, fuzzy_autocomplete

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

import os


def setup_names():
    folder_path = 'static/images/setups'
    file_names = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.png'):
            file_names.append(file_name[:-4])  # Remove the '.png' from the end

    return file_names


class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @discord.slash_command(name="help", description="A list of all my cool commands!")
    async def help(self, ctx: discord.ApplicationContext):
        commands_info = {
            "help": "A list of all my cool commands!",
            "dink": "Use this command to get help setting up your dink plugin.",
            "player": "Get a bunch of data about a player in the bingo.",
            "team": "Get a bunch of data about a team in the bingo.",
            "progress": "Check your progress on a specific tile.",
            "board": "Get a list of tiles you've already completed.",
            "leaderboard": "Show the current standings amongst teams and players."
        }

        response = "**Here are all my available commands:**\n\n"
        for command, description in commands_info.items():
            response += f"/{command} - {description}\n"

        await ctx.respond(response)

    @discord.slash_command(name="dink", description="Use this command to get help setting up your dink plugin")
    async def dink(self, ctx:discord.ApplicationContext):
        await ctx.defer()
        server_ip = os.getenv('SERVER_IP')
        player_url = f"http://{server_ip}/tutorial/dink"
        await ctx.respond(player_url)

    @discord.slash_command(name="player", description="Get a bunch of data about a player in the bingo")
    async def player(self, ctx: discord.ApplicationContext,
                     player_name: discord.Option(str, "What is the username?", autocomplete=lambda ctx: fuzzy_autocomplete(ctx, player_names()))):
        await ctx.defer()
        server_ip = os.getenv('SERVER_IP')
        player_url = f"http://{server_ip}/user/player/{player_name.replace(' ', '%20')}"
        await ctx.respond(player_url)

    @discord.slash_command(name="team", description="Get a bunch of data about a team in the bingo")
    async def team(self, ctx: discord.ApplicationContext,
                   team_name: discord.Option(str, "What is the team name?", autocomplete=lambda ctx: fuzzy_autocomplete(ctx, team_names()))):
        await ctx.defer()
        server_ip = os.getenv('SERVER_IP')
        team_url = f"http://{server_ip}/user/team/{team_name.replace(' ', '%20')}"
        await ctx.respond(team_url)


    @discord.slash_command(name="gear", description="View our catalog of gear setups for any content and budget")
    async def gear(self, ctx: discord.ApplicationContext,
                   setup: discord.Option(str, "What setup are you looking for?",
                                         autocomplete=lambda ctx: fuzzy_autocomplete(ctx, setup_names()))):

        base_url = "https://danbot.up.railway.app/static/images/setups/"
        file_name = f"{setup}.png"
        escaped_file_name = urllib.parse.quote(file_name)
        url = f"## {setup}\n{base_url}{escaped_file_name}"

        await ctx.respond(url)
    @discord.slash_command(name="progress", description="Check your progress on a specific tile")
    async def progress(self, ctx:discord.ApplicationContext,
                       team_name: discord.Option(str, "What is your team name?", autocomplete=lambda ctx: fuzzy_autocomplete(ctx, team_names())),
                       tile_name: discord.Option(str, "What tile are you checking?", autocomplete=lambda ctx: fuzzy_autocomplete(ctx, tile_names()))):
        await ctx.defer()
        team = db_entities.Team(database.get_team_by_name(team_name))
        tile = db_entities.Tile(database.get_tile_by_name(tile_name))
        progress = bingo.check_progress(tile, team)
        if progress is None:
            await ctx.respond(f"You have fully completed {tile.tile_name}!")
        else:
            await ctx.respond(progress)

    @discord.slash_command(name="board", description="Get a list of tiles you've already completed")
    async def board(self, ctx:discord.ApplicationContext,
                    team_name: discord.Option(str, "What is your team name?", autocomplete=lambda ctx: fuzzy_autocomplete(ctx, team_names())),
                    board_type: discord.Option(str, "What kind of board would you like to see?", autocomplete=discord.utils.basic_autocomplete(["All Tiles","Completed Tiles","Incomplete Tiles", "Partial Tiles"]))):
        await ctx.defer()
        response = f"## {board_type} for {team_name}\n"
        team = db_entities.Team(database.get_team_by_name(team_name))
        tiles = database.get_tiles()
        completed_tiles = database.get_completed_tiles()
        complete_tile_dict = defaultdict(int)
        for tile in completed_tiles:
            tile = db_entities.CompletedTile(tile)
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
                    response = response + "\n"
        elif board_type == "Partial Tiles":
            for tile in tiles:
                tile = db_entities.Tile(tile)
                progress = bingo.check_progress(tile, team)
                if progress is not None:
                    response = response + progress

        await ctx.respond(response)

    @discord.slash_command(name="leaderboard", description="Show the current standings amongst teams and players")
    async def leaderboard(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        server_ip = os.getenv('SERVER_IP')
        leaderboard_url = f"http://{server_ip}/user/leaderboard"
        await ctx.respond(leaderboard_url)