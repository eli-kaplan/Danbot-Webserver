import os

import discord


from cogs.AdminCog import AdminCog
from cogs.UserCog import UserCog

bot = discord.Bot()
token = os.getenv('DISCORD_BOT_TOKEN')



def run():
    bot.add_cog(UserCog(bot))
    bot.add_cog(AdminCog(bot))
    bot.run(token)

