import discord
from discord.ext import commands
from discord import default_permissions, guild_only



class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="secret_command", description="Just checking permissions")
    @default_permissions(manage_webhooks=True)
    @guild_only()
    async def secret_command(self, ctx):
        await ctx.respond('Hello, admin!')
