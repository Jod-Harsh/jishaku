import typing

import discord
from discord.ext import commands


class Dropdown(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(label='CUSTOM BOT', description='Choose your favourite owner', emoji='<a:CROWN:929105520080609310>'),
        ]

        super().__init__(custom_id='CUSTOM BOT',placeholder='Want To Buy YoUr Own Bot ?', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):

        await interaction.response.send_message(f'**DM <@924589827586928730> TO BUY YOUR OWN CUSTOM BOT OK !! \n PRICE 1.5K FOR BOT AND AFTER 1 MONTH 800 INR PER MONTH HOSTING CHARGE**', ephemeral=True)