import discord
import discord.ui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import asyncio
from datetime import datetime

FORMAT = ['Min', 'P25']
EQUIP = {
    'helmet': ['helm'],
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
    'att': ['attack'],
    'matt': ['magic'],
    'avoidability': ['avoid'],
    'accuracy': ['acc'],
    'def': ['defense'],
    'weapon def.': ['wdef'],
    'magic def.': ['mdef']
}
PERCENT = {'10%' : '10', '60%' : '60', '100%' : '100', '30%' : '30', '70%' : '70'}

PRICE = {}

with open('token.txt', 'r') as file:
    TOKEN = file.read().strip()
intents = discord.Intents.default()
intents.message_content = True

options = webdriver.ChromeOptions()
options.add_argument("--headless")
service = Service('chromedriver-linux64/chromedriver')
driver = webdriver.Chrome(service=service, options=options)

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    pricefile = open("price.txt", "r")
    for line in pricefile:
        elements = line.strip().split(',')
        PRICE[elements[0]] = (elements[1], elements[2])
    pricefile.close
    print('Price Loaded!')
    print(PRICE)
    print()
    print(f'Logged in as {bot.user}')
    await bot.change_presence(status=discord.Status.idle, activity=discord.CustomActivity('Hoot Hoot'))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('!owl'):
        input = " ".join(message.content.split(' ')[1:])
        if not input:
            await message.channel.send(f'{message.author.mention}, use "!owl itemname" to search for an item.')
        else:
            file = discord.File('owl.png')
            input = input_modify(input)
            data = get_price(input)
            embed = format_answer(input, data)
            
            field_names = [field.name.strip("*") for field in embed.fields]
            select_options = [discord.SelectOption(label=name, value=name) for name in field_names]
            select = discord.ui.Select(
                placeholder="Update min price",
                options=select_options
            )
            view = discord.ui.View()
            view.add_item(select)
            msg = await message.reply(file=file, embed=embed, view=view)
            select.callback = bot.on_select_option

@bot.event
async def on_select_option(interaction):
    selected_option = interaction.data['values'][0]
    await interaction.response.send_message(f'How would you like to update the min price of {selected_option}?')
    try:
        response = await bot.wait_for('message', check=lambda m: m.author == interaction.user, timeout=15.0)
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
    update_price(selected_option, formatted_price)
    await interaction.followup.send(f'Min price updated to {formatted_price}')

def input_modify(input):
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

def get_price(input):
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
        if item: 
            items.append(item)
    return items

def format_answer(input, data):
    embed = discord.Embed(title=input, colour=0x3498DB)
    embed.set_thumbnail(url='attachment://owl.png')
    data = [[row[i].strip() for i in [0, 1, 5, 6]] for row in data]
    data = [check_pricedict(row) for row in data]
    names = [row[0] for row in data]
    dates = [row[1] for row in data]
    data = [[row[i] for i in [2, 3]] for row in data]
    for row in range(len(data)):
        value = ""
        value += dates[row] + '\n'
        for i in range(len(FORMAT)):
            element = f'{FORMAT[i]}: {data[row][i]} '
            value += element + '\n'
        embed.add_field(name=f"**{names[row]}**", value=value)
    current_time = datetime.now().strftime("%Y-%m-%d")
    embed.set_footer(text=f'{current_time}')
    return embed

def update_price(itemname, price):
    current_date = datetime.now().strftime("%Y-%m-%d")
    PRICE[itemname] = (current_date, price)
    write_pricefile()

def write_pricefile():
    pricefile = open("price.txt", 'w')
    for key, value in PRICE.items():
        line = key + ',' + value[0] + ',' + value[1] + '\n'
        pricefile.write(line)
    pricefile.close

def check_pricedict(rowlist):
    [itemname, date, min, p25] = rowlist
    for key, value in PRICE.items():
        if key == itemname:
            owlrepo_date = datetime.strptime(date, "%Y-%m-%d")
            dict_date = datetime.strptime(value[0], "%Y-%m-%d")
            if dict_date >= owlrepo_date:
                return [itemname, dict_date.strftime("%Y-%m-%d"), value[1], '---']
    return [itemname, date, min, p25]
                
bot.run(TOKEN)