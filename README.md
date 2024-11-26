# Owlrepo-Discord-Bot

A Discord bot that helps users search and manage item prices on owlrepo.com.

![image](https://github.com/woogyeom/Owlrepo-Discord-Bot/assets/17395464/a39261d4-1f26-4d33-b592-37aac2f5471e)

## Project Overview
Owlrepo-Discord-Bot allows players to quickly search for item prices on [owlrepo.com](https://owlrepo.com) and update the data with the latest market prices, all within Discord. The bot also provides auto-completion for scroll names to make item searches easier.

## Key Features
- **Price Search**: Retrieve item prices from owlrepo.com directly within Discord using the `!owl` command.
- **Auto-Completion for Scroll Names**: Automatically complete scroll names when searching (e.g., `!owl overall int 10` will become `scroll for overall armor for int 10%`).
- **Price Update Interaction**: Update the minimum price of an item interactively using Discord's built-in UI elements.

## How to Use
- **Search for Item Prices**: Use `!owl itemname` to look up the price of an item.
  - Example: `!owl helmet str 60`
- **Update Item Prices**: Select an item from the response to update its minimum price with the latest information you have.

## Technologies Used
- **Python**
- **Discord.py**
- **Selenium**: Used to automate item price searches on owlrepo.com.
