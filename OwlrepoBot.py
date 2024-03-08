import discord
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

FORMAT = ['Min', 'P25']
EQUIP = {'helmet' : 'helm',
         'face accessory' : ['face', 'faceacc'],
         'eye accessory' : ['eye', 'eyeacc'],
         'earring' : ['ear', 'earrings'],
         'overall armor' : 'overall',
         'topwear' : ['top'],
         'bottomwear' : ['bottom', 'bot'],
         'gloves' : ['glove'],
         'shoes' : ['shoe'],
         'cape' : [],
         'shield' : [],
         'one-handed sword' : ['1hs'],
         'two-handed sword' : ['2hs'],
         'one-handed bw' : ['1hb', '1hbw'],
         'two-handed bw' : ['2hb', '2hbw'],
         'one-handed axe' : ['1ha'],
         'two-handed axe' : ['2ha'],
         'spear' : [],
         'polearm' : ['pole'],
         'bow' : [],
         'crossbow' : ['xbow'],
         'wand' : [],
         'staff' : [],
         'claw' : [],
         'dagger' : ['dag'],
         'gun' : [],
         'knuckler' : ['knuckle', 'kn']
         }
STAT = ['str', 'dex', 'int', 'luk', 'hp', 'mp', 'att', 'matt', 'avoid', 'acc']
PERCENT = {'10%' : '10', '60%' : '60', '100%' : '100', '30%' : '30', '70%' : '70'}

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
            input = " ".join(message.content.split(' ')[1:])
            if not input:
                await message.channel.send(f'{message.author.mention} , do "!owl itemname" u dumb')
            else:
                file = discord.File('owl.png')
                input = self.input_modify(input)
                print(input)
                data = self.get_price(input)
                embed = self.format_answer(input, data)
                await message.reply(file=file, embed=embed)

    def input_modify(self, input):
        input_split = input.lower().split()
        modified = ""

        for i, word in enumerate(input_split):
            for equip, aliases in EQUIP.items():
                if word == equip or word in aliases:
                    print(word)
                    next_index = i + 1
                    if next_index < len(input_split) and input_split[next_index] in STAT:
                        modified = f"scroll for {equip} for {input_split[next_index]}"
                        print(word, modified)
                        next_next_index = next_index + 1
                        if next_next_index < len(input_split):
                            percent_word = input_split[next_next_index]
                            for percent, value in PERCENT.items():
                                if percent_word == percent or percent_word == value:
                                    if percent == '30%' or percent == '70%':
                                        modified = 'dark ' + modified
                                    modified += f" {percent}"
                                    print(percent_word, modified)

        if modified:
            return modified
        return input


    def get_price(self, input):
        url = 'https://owlrepo.com/summary'
        driver.get(url)
        
        search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="search-box"]'))
        )
        search_box.send_keys(input)

        items = []
        for row in range(1, 10):
            item = []
            for cell in range(1, 12):
                xpath = f'/html/body/main/div[2]/div[2]/div/div[{row}]/div[{cell}]'
                try:
                    element = driver.find_element(By.XPATH, xpath) 
                    if element:
                        item.append(element.text)
                except NoSuchElementException:
                    break
            if item: items.append(item)
        #print(items)
        return items
    
    def format_answer(self, input, data):
        embed = discord.Embed(title=input, colour=0x3498DB)
        embed.set_thumbnail(url='attachment://owl.png')
        names = [row[0] for row in data]
        dates = [row[1] for row in data]
        data = [[row[i] for i in [5, 6]] for row in data]

        for row in range(len(data)):
            value = ""
            value += dates[row] + '\n'
            for i in range(len(FORMAT)):
                element = f'{FORMAT[i]}: {data[row][i]} '
                value += element + '\n'

            embed.add_field(name=f"**{names[row]}**", value=value)
        return embed

bot = MyClient(intents=intents)
bot.run(TOKEN)