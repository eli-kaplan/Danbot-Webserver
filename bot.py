import os

import discord


from cogs.AdminCog import AdminCog
from cogs.SubmitRequestCog import SubmitRequestCog
from cogs.UserCog import UserCog
from discord.ext import commands

bot = discord.Bot()
token = os.getenv('DISCORD_BOT_TOKEN')



def run():
    bot.add_cog(UserCog(bot))
    bot.add_cog(AdminCog(bot))
    bot.add_cog(SubmitRequestCog(bot))
    bot.run(token)

