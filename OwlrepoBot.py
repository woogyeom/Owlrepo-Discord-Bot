import discord
import discord.ui
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import asyncio
import datetime

FORMAT = ['Min', 'P25']
EQUIP = {
    'helmet': 'helm',
    'face accessory': ['face'],
    'eye accessory': ['eye'],
    'earring': ['ear', 'earrings'],
    'overall armor': 'overall',
    'topwear': ['top'],
    'bottomwear': ['bottom', 'bot'],
    'gloves': ['glove'],
    'shoes': ['shoe'],
    'cape': [],
    'shield': [],
    'one-handed sword': ['1hs'],
    'two-handed sword': ['2hs'],
    'one-handed bw': ['1hb', '1hbw'],
    'two-handed bw': ['2hb', '2hbw'],
    'one-handed axe': ['1ha'],
    'two-handed axe': ['2ha'],
    'spear': [],
    'polearm': ['pole'],
    'bow': [],
    'crossbow': ['xbow'],
    'wand': [],
    'staff': [],
    'claw': [],
    'dagger': ['dag'],
    'gun': [],
    'knuckler': ['knuckle', 'kn']
}
STAT = {
    'str': [],
    'dex': [],
    'int': [],
    'luk': [],
    'hp': [],
    'mp': [],
    'speed': [],
    'jump': [],
    'att': [],
    'matt': [],
    'avoidability': 'avoid',
    'accuracy': 'acc',
    'def': [],
    'weapon def.': 'wdef',
    'magic def.': 'mdef'
}
PERCENT = {'10%' : '10', '60%' : '60', '100%' : '100', '30%' : '30', '70%' : '70'}

with open('token.txt', 'r') as file:
    TOKEN = file.read().strip()
intents = discord.Intents.default()
intents.message_content = True
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())) 

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.change_presence(status=discord.Status.idle, activity=discord.CustomActivity('Hoot Hoot'))
    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith('!owl'):
            input = " ".join(message.content.split(' ')[1:])
            if not input:
                await message.channel.send(f'{message.author.mention}, use "!owl itemname" to search for an item.')
            else:
                file = discord.File('owl.png')
                input = self.input_modify(input)
                data = self.get_price(input)
                embed = self.format_answer(input, data)
                
                field_names = [field.name.strip("*") for field in embed.fields]
                select_options = [discord.SelectOption(label=name, value=name) for name in field_names]
                select = discord.ui.Select(
                    placeholder="Update min price",
                    options=select_options
                )
                view = discord.ui.View()
                view.add_item(select)
                msg = await message.reply(file=file, embed=embed, view=view)
                select.callback = self.on_select_option
    async def on_select_option(self, interaction):
        selected_option = interaction.data['values'][0]
        await interaction.response.send_message(f'How would you like to update the min price of {selected_option}?')
        try:
            response = await self.wait_for('message', check=lambda m: m.author == interaction.user, timeout=10.0)
            new_price = int(response.content)
        except asyncio.TimeoutError:
            await interaction.followup.send('You took too long to respond. Please try again.')
            return
        except ValueError:
            await interaction.followup.send('Invalid input.')
            return
        if new_price >= 1_000_000:
            formatted_price = f'{new_price / 1_000_000:.1f}m'
        elif new_price >= 1_000:
            formatted_price = f'{new_price // 1_000:.0f}k'
        else:
            formatted_price = f'{new_price:.0f}'
        self.update_price(selected_option, formatted_price)
        await interaction.followup.send(f'Min price updated to {formatted_price}')

    def input_modify(self, input):
        input_split = input.lower().split()
        modified = ""
        for i, word in enumerate(input_split):
            for equip, aliases in EQUIP.items():
                if word == equip or word in aliases:
                    next_index = i + 1
                    if next_index < len(input_split) and input_split[next_index] == 'for':
                        next_index += 1
                    if next_index < len(input_split):
                        stat_word = input_split[next_index]
                        for stat, s_aliases in STAT.items():
                            if stat_word == stat or stat_word in s_aliases:
                                stat_word = stat
                                if stat_word == 'matt': stat_word = 'magic att.'
                                if equip == 'shield' and stat_word == 'att': stat_word = 'weapon att.'
                                modified = f"scroll for {equip} for {stat_word}"
                                next_next_index = next_index + 1
                                if next_next_index < len(input_split):
                                    percent_word = input_split[next_next_index]
                                    for percent, value in PERCENT.items():
                                        if percent_word == percent or percent_word == value:
                                            if percent == '30%' or percent == '70%':
                                                modified = 'dark ' + modified
                                            modified += f" {percent}"
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
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        embed.set_footer(text=f'{current_time}')
        return embed
    
    def update_price(self, itemname, price):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                

bot = MyClient(intents=intents)
bot.run(TOKEN)