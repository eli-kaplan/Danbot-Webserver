from discord.ext import commands
import discord

from utils import database, db_entities
from discord import default_permissions, guild_only


class SubmitRequestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.message_command(name="submit_tile")
    async def submit_tile_request(self, ctx, message: discord.Message):
        modal = SubmitRequestModal(message=message)
        await ctx.send_modal(modal)

    @discord.slash_command(name="requests", description="Check if any requests need to be verified")
    @guild_only()
    @default_permissions(manage_webhooks=True)
    async def requests(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        request = database.get_request()
        if request is not None:
            request = db_entities.Request(request)

            embed = discord.Embed(title="Request", colour=discord.Colour.magenta())

            embed.add_field(name="Team Name", value=request.team_name[0])
            embed.add_field(name="Player Name", value=request.player_name[0])
            embed.add_field(name="Tile Name", value=request.tile_name[0])
            embed.add_field(name="Item Description", value=request.item_name)
            try:
                embed.set_image(url=request.evidence)
            except:
                embed.add_field(name="Evidence", value=request.evidence)
            await ctx.respond(embed=embed, view=RequestView(request))
        else:
            await ctx.respond("There are no requests currently open")


class RequestView(discord.ui.View):
    def __init__(self, request):
        super().__init__()
        self.request = request
        self.timeout = None

    @discord.ui.button(label="I resolved this request", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        button.disabled = True
        self.disable_all_items()
        database.delete_request(self.request.request_id)
        await interaction.response.edit_message(content=f"Request resolved and deleted :white_check_mark:", embed=None,
                                                view=None)

    @discord.ui.button(label="Stash this request for later", row=0, style=discord.ButtonStyle.danger)
    async def second_button_callback(self, button, interaction):
        button.disabled = True
        self.disable_all_items()
        await interaction.response.edit_message(content=f"This request has been stashed to be checked later",
                                                embed=None, view=None)


class SubmitRequestModal(discord.ui.Modal):
    def __init__(self, message, *args, **kwargs) -> None:
        super().__init__(title="Submit Tile Request", *args, **kwargs)
        self.message = message
        self.add_item(discord.ui.InputText(label="Team name:"))
        self.add_item(discord.ui.InputText(label="Player name:"))
        self.add_item(discord.ui.InputText(label="Tile name:"))
        self.add_item(discord.ui.InputText(label="Item Description:"))
        try:
            self.image = message.attachments[0].url
        except:
            self.image = message.content

    async def callback(self, interaction: discord.Interaction):
        try:
            database.add_request(
                self.children[0].value,  # Team name
                self.children[1].value,  # Player name
                self.children[2].value,  # Tile name
                self.children[3].value,  # Item Description
                self.image
            )
            await interaction.response.send_message(
                content="Request received. Wait for an admin to view and approve it :white_check_mark:"
            )
        except Exception as e:
            await interaction.response.send_message(content=f"Unknown value {e.args[0]} :x:")
