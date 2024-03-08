import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup

last_scraped = ""

TOKEN = 'MTIxNTUwNjYzMTI0OTM2NzA0MA.Ghy32d.dbSaIgIKTduijqjIHiF43-mU3hjpLckCBAb0tk'

intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith('!owl'):
            #await message.channel.send("yoyo")
            itemname = message.content.split(' ')[1:]
            if not itemname:
                await message.channel.send("do !owl itemname u dumb")
            else:
                await message.channel.send(itemname)

    def get_items(self, itemname):
        pass

    def get_price(self, itemname):
        pass

bot = MyClient(intents=intents)
bot.run(TOKEN)