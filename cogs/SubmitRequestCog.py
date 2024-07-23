from discord.ext import commands
import discord

from utils import database, db_entities
from discord import default_permissions, guild_only


class SubmitRequestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.message_command(name="submit_tile")
    async def submit_tile_request(self, ctx, message: discord.Message):
        modal = SubmitRequestModal(message=message)  # .attachments[0], title="Submit Tile Request")
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


class SubmitRequestView(discord.ui.View):
    def __init__(self, team_name, player_name, tile_name, item_description, image):
        super().__init__()
        self.image = image
        self.team_name = team_name
        self.player_name = player_name
        self.tile_name = tile_name
        self.item_description = item_description
        self.timeout = None

    @discord.ui.button(label="Yes", row=0, style=discord.ButtonStyle.primary)
    async def first_button_callback(self, button, interaction):
        self.disable_all_items()
        try:
            database.add_request(self.team_name, self.player_name, self.tile_name, self.item_description, self.image)
            await interaction.response.edit_message(
                content=f"Your request has been submitted :white_check_mark:\nAn officer will review it soon",
                view=None, embed=None)
        except Exception as e:
            await interaction.response.edit_message(content=f"Unknown value {e.args[0]} :x: ", view=None,
                                                    embed=None)

    @discord.ui.button(label="No", row=0, style=discord.ButtonStyle.danger)
    async def second_button_callback(self, button, interaction):
        self.disable_all_items()
        button.label = "Request closed"
        await interaction.response.edit_message(view=self)


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
        embed = discord.Embed(title="Does this look right to you?")
        embed.add_field(name="Team Name", value=self.children[0].value)
        embed.add_field(name="Player Name", value=self.children[1].value)
        embed.add_field(name="Tile Name", value=self.children[2].value)
        embed.add_field(name="Item Description", value=self.children[3].value)
        try:
            embed.set_image(url=self.image)
        except:
            embed.add_field(name="Message content:", value=self.message.content)
        await interaction.response.send_message(embed=embed,
                                                view=SubmitRequestView(self.children[0].value, self.children[1].value,
                                                                       self.children[2].value, self.children[3].value,
                                                                       self.image))
