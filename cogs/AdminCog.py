import sqlite3

import discord
from discord.ext import commands
from discord import default_permissions, guild_only

import database
import utils.autocomplete
from routes import dink
from utils import spoof_drop, scapify
from utils.autocomplete import *
from utils.send_webhook import send_webhook


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="secret_command", description="Just checking permissions")
    @default_permissions(manage_webhooks=True)
    @guild_only()
    async def secret_command(self, ctx):
        await ctx.respond('Hello, admin!')

    @discord.slash_command(name="award_drop", description="Manually award a drop")
    @default_permissions(manage_webhooks=True)
    @guild_only()
    async def award_drop(self, ctx:discord.ApplicationContext,
                         player_name: discord.Option(str, "What is the username?", autocomplete=lambda ctx: fuzzy_autocomplete(ctx, player_names())),
                         drop_name: discord.Option(str, "What is the drop name?", autocomplete=lambda ctx: fuzzy_autocomplete(ctx, drop_names())),
                         quantity: discord.Option(int, "How many drops did they get?", default=1),
                         drop_value: discord.Option(int, "How much is each drop worth?", default=0)):
        await ctx.defer()
        json_data = spoof_drop.award_drop_json(player_name, drop_name, drop_value, quantity)
        result = dink.parse_loot(json_data, None)

        if result:
            await ctx.respond(f"Successfully awarded {player_name} with {quantity} x {drop_name} at {scapify.int_to_gp(drop_value)} each")
        else:
            await ctx.respond(f"Something went wrong. Check my console or contact Danbis before attempting again.")

    @discord.slash_command(name="run_query", description="DANGER! IF YOU'RE NOT DANBIS OR DON'T KNOW WHAT YOUR DOING DON'T RUN THIS COMMAND")
    @default_permissions(manage_webhooks=True)
    @guild_only()
    async def run_query(self, ctx:discord.ApplicationContext,
                        query: discord.Option(str)):
        await ctx.defer()
        with sqlite3.connect('my_database.db') as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            await ctx.respond(f"Executed query: ```{query}```\nResponse data: ```{cursor.fetchall()}```")

    @discord.slash_command(name="award_niche_progress", description="Add tile progress to a niche tile")
    @default_permissions(manage_webhooks=True)
    @guild_only()
    async def award_niche_progress(self,
                                   ctx: discord.ApplicationContext,
                                   player_name: discord.Option(str, "What is the players name?", autocomplete=lambda ctx: fuzzy_autocomplete(ctx, player_names())),
                                   tile_name: discord.Option(str, "What is the tile_name?", autocomplete=lambda ctx: fuzzy_autocomplete(ctx, niche_tile_names())),
                                   progress: discord.Option(int, "What trigger value would you like to add?")):
        await ctx.defer()
        database.add_niche_progress(tile_name, player_name, progress)
        tile = db_entities.Tile(database.get_tile_by_name(tile_name))
        player = db_entities.Player(database.get_player_by_name(player_name))
        team = db_entities.Team(database.get_team_by_id(player.team_id))
        tile_completions = len(database.get_completed_tiles_by_team_id_and_tile_id(player.team_id, tile.tile_id))
        if tile_completions >= tile.tile_repetition:
            response = f"This tile has already been completed {tile.tile_repetition} times. There is no point in awarding more progress."
            ctx.respond(response)
            return

        database.add_player_tile_completions(player.player_id, progress/tile.tile_triggers_required)
        response = f"Successfully added {progress} trigger weight to {tile.tile_name} for {player.player_name}'s team. Additionally I've given {player.player_name} {round(progress/tile.tile_triggers_required, 2)} tile completions"
        progress = database.get_niche_progress_by_tile_id_and_team_id(tile.tile_id, player.team_id)
        if progress >= (tile_completions + 1) * tile.tile_triggers_required:
            database.add_completed_tile(tile.tile_id, player.team_id)
            database.add_team_points(player.team_id, tile.tile_points)
            if int(progress % tile.tile_triggers_required) == tile.tile_triggers_required:
                progress = 0
            send_webhook(team.team_webhook, title=f"{tile.tile_name} completed!", description=f"You now have {tile_completions + 1} completions and are {int(progress % tile.tile_triggers_required)}/{tile.tile_triggers_required} from your next completion", color=65280, image=None)
            response = response + f"\nIt seems they have also completed this tile so I've awarded them {tile.tile_points} points and sent them a message letting them know! They now have {tile_completions + 1} completions for this tile"
        else:
            send_webhook(team.team_webhook, title=f"Request approved for {tile.tile_name}!", description=f"You are now {int(progress % tile.tile_triggers_required)}/{tile.tile_triggers_required} away from completing this tile", color=16776960, image=None)

        await ctx.respond(response)