from secret import *
if TOKEN == "past your token here":
    print("please, past your token in secret.py")
    exit()
import discord
from discord.ext import commands
import os


cogs = ["commands", "fight"]

class MyBot(commands.Bot):
    def __init__(self):
        __author = 487876087330635810
        super().__init__(command_prefix='f/', intents=discord.Intents.all())

    async def setup_hook(self):
        for cog in cogs:
            await self.load_extension(cog)
            await bot.tree.sync()

    async def on_message(self, message):
        msg = message.content
        if msg == "f/reload":
            for cog in cogs:
                try:
                    await self.unload_extension(cog)
                    await message.channel.send(f"Ког {cog} выгружен")
                except:
                    await message.channel.send(f"Ког {cog} не был загружен")
                await self.load_extension(cog)
            await message.channel.send(f"Все коги запущены")
            await bot.tree.sync()
        if msg == "f/test":
            await message.channel.send("test")

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')


bot = MyBot()
bot.run(TOKEN)