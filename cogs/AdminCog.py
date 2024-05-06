import sqlite3

import discord
from discord.ext import commands
from discord import default_permissions, guild_only

from routes import dink
from utils import spoof_drop, scapify
from utils.autocomplete import *


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
                         player_name: discord.Option(str, "What is the username?", autocomplete=discord.utils.basic_autocomplete(player_names)),
                         drop_name: discord.Option(str, "What is the drop name?", autocomplete=discord.utils.basic_autocomplete(drop_names)),
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