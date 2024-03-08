import discord
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

EQUIP = ['helmet', 'face', 'eye', 'ear', 'cape', 'top', 'gloves', 'bottom', 'shoes', '1hs', '1hb', '1ha', '2hs', '2hb', '2ha', 'spear', 'pole', 'bow', 'xbow', 'wand', 'staff', 'dagger', 'claw', 'gun', 'knucle', 'shield']
STAT = ['str', 'dex', 'int', 'luk', 'hp', 'mp', 'speed', 'jump', 'acc', 'avoid', 'att', 'matt', 'def', 'mdef']
SCROLL = ['10%', '30%', '60%', '70%', '100%']

with open('token.txt', 'r') as file:
    TOKEN = file.read().strip()

intents = discord.Intents.default()
intents.message_content = True

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) 

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.change_presence(status=discord.Status.idle, activity=discord.Game('Hoot Hoot'))
    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith('!owl'):
            itemname = message.content.split(' ')[1:]
            if not itemname:
                await message.channel.send(f'{message.author.mention} , do "!owl itemname" u dumb')
            else:
                price = self.get_price(itemname)
                embed = self.format_answer(price)
                await message.channel.send(embed=embed)

    def get_items(self, itemname):
        pass

    def check_scroll(self, itemname):
        if itemname[0].lower in EQUIP:
            if itemname[1].lower in STAT:
                if len(itemname) >= 3:
                    if itemname[2] in SCROLL:
                        # scroll with %
                        if itemname[2] == '30%' or '70%':
                            result += 'Dark '
                        result += 'scroll for ' + itemname[0] + 'for ' + itemname[1] + ' ' + itemname[2]
                        pass
                    else:
                        # scroll without %
                        result = []
                        pass
        else:
            return itemname

    def get_price(self, itemname):
        url = 'https://owlrepo.com/items?keyword=' + '%20'.join(itemname)
        driver.get(url)
        time.sleep(1)

        row = driver.find_element(By.XPATH, '/html/body/main/div[1]/div[2]/div/div[1]')
        result = row.text.splitlines()[:2]
        result.append(row.text.splitlines()[8])

        return result
    
    def format_answer(self, result):
        desc = '**Updated**: ' + result[0] + '\n**Min Price**: ' + result[2]
        embed = discord.Embed(title=result[1], description=desc)
        return embed

bot = MyClient(intents=intents)
bot.run(TOKEN)