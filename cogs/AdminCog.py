import discord
from discord.ext import commands

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        # Replace 'Admin' with the name of the role that should have access
        return 'Bingo Moderator' in [role.name for role in ctx.author.roles]

    @discord.slash_command(name="secret_command", description="Just checking permissions")
    async def secret_command(self, ctx):
        await ctx.respond('Hello, admin!')
