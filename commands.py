import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.app_commands import Choice
import os
import json 
import sqlite3
from random import randint

class cmds(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot 
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game('RolePlay дуэли'))

    @app_commands.command(name="автор", description="Автор бота")
    async def author_send(self, interaction: discord.Interaction) -> None:
        author = await self.bot.fetch_user(487876087330635810)
        await interaction.response.send_message(f"Автор бота: {author}")

    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            emb = discord.Embed(title="Ошибка", description='У вас недостаточно прав на выполнение данной команды!', colour = 0x333333)
            await ctx.response.send_message(embed=emb, ephemeral = True)
		    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(cmds(bot))
        