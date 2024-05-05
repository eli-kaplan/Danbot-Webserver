import os

import discord
from discord import default_permissions, guild_only

import database
import db_entities
import utils.scapify
from cogs.AdminCog import AdminCog
from cogs.UserCog import UserCog
from utils.autocomplete import player_names

bot = discord.Bot()
token = os.getenv('DISCORD_BOT_TOKEN')



def run():
    bot.add_cog(UserCog(bot))
    bot.add_cog(AdminCog(bot))
    bot.run(token)

