import os

import discord


from cogs.AdminCog import AdminCog
from cogs.SubmitRequestCog import SubmitRequestCog
from cogs.UserCog import UserCog
from discord.ext import commands

bot = discord.Bot()
token = os.getenv('DISCORD_BOT_TOKEN')


@bot.event
async def on_guild_join(guild):
    # Your code here
    # approved_guilds = set()

    # Approved guilds
    # approved_guilds.add(714260066072657980) # W22 Fish

    # if guild.id not in approved_guilds:
    await guild.leave()




def run():
    bot.add_cog(UserCog(bot))
    bot.add_cog(AdminCog(bot))
    bot.add_cog(SubmitRequestCog(bot))
    bot.run(token)

