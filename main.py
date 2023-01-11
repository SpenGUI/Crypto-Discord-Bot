# This script creates a simple trading bot for Discord using the ccxt library and the Discord.py library.
# The bot allows users to subscribe to Bitcoin price alerts and receive notifications when the price changes by more than a certain threshold.
# The bot also includes commands for stopping the alerts and shutting down the bot.
# The bot uses the Binance exchange to fetch the current price of Bitcoin, but you can easily modify it to use other exchanges supported by ccxt.

import discord
from discord.ext import commands
from discord import app_commands
import ccxt
import time

# Replace YOUR_BOT_TOKEN with your actual bot token
bot = commands.Bot(command_prefix=['!', '/'], description='A simple trading bot', intents=discord.Intents.all())

# Connect to the cryptocurrency exchange
exchange = ccxt.binance()

# Define the threshold for price changes (in percentage)
THRESHOLD = 0.000000000000000000000000000001

# A list to store the subscribers
subscribers = []

# Discord server and channel ID
SERVER_ID = "1061460237254672404"
CHANNEL_ID = "1061460237254672404"
ROLE_NAME = "BitCoin Subscriber"

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(name="subscribe", description = "Subscribe to see bitcoin Alerts!")
async def subscribe(ctx):
    """Subscribe to Bitcoin price alerts"""
    # Add the user to the list of subscribers
    if ctx.message.author not in subscribers:
        subscribers.append(ctx.message.author)
        role = discord.utils.get(ctx.guild.roles, name=ROLE_NAME)
        await ctx.message.author.add_roles(role)
        await ctx.send(f'{ctx.message.author.display_name} you are now subscribed to Bitcoin price alerts and have been given the BitCoin Subscriber role')
    else:
        await ctx.send(f'{ctx.message.author.display_name} you are already subscribed to Bitcoin price alerts')


@bot.command(name="unsubscribe", description = "Unsubscribe from Bitcoin price alerts")
async def unsubscribe(ctx):
    # Remove the user from the list of subscribers
    if ctx.message.author in subscribers:
        subscribers.remove(ctx.message.author)
        role = discord.utils.get(ctx.guild.roles, name="BitCoin Subscriber")
        await ctx.message.author.remove_roles(role)
        await ctx.send(f'{ctx.message.author.display_name} you are now unsubscribed from Bitcoin price alerts and the BitCoin Subscriber role has been removed')
    else:
        await ctx.send(f'{ctx.message.author.display_name} you are not subscribed to Bitcoin price alerts')


running = False


is_alerts_running = False

@bot.command(name="alerts", description = "Start checking the price of Bitcoin and alerting subscribers if it changes by more than " + str(THRESHOLD) + "%")
async def alerts(ctx):
    global running
    global is_alerts_running
    is_alerts_running = True
    running = True
    channel = bot.get_channel(CHANNEL_ID)
    ticker = exchange.fetch_ticker('BTC/GBP')
    current_price = ticker['last']
    while running:
        time.sleep(30)
        ticker = exchange.fetch_ticker('BTC/GBP')
        latest_price = ticker['last']
        change = ((latest_price - current_price) / current_price) * 100
        if change > THRESHOLD:
            for user in subscribers:
                user.send(f"Stonks (Change: {change:.2f}% current Value: {latest_price:.2f})")
            await channel.send(f"Stonks (Change: {change:.2f}% current Value: {latest_price:.2f})")
        elif change < -THRESHOLD: 
            for user in subscribers:
                               user.send(f"Not Stonks (Change: {change:.2f}% current Value: {latest_price:.2f})")
            await channel.send(f"Not Stonks (Change: {change:.2f}% current Value: {latest_price:.2f})")

        print("cycle done!")
        time.sleep(30)
    is_alerts_running = False

@bot.command(name="stop", description = "Stop checking the price of Bitcoin")
async def stop(ctx):
    global running
    running = False

@bot.command(aliases=["quit"])
@commands.has_permissions(administrator=True)
async def shutdown(ctx):
    global is_alerts_running
    await ctx.channel.send("Shutting down...")
    if is_alerts_running:
        global running
        running = False
        await ctx.send("Stopping alerts loop and shutting down the bot...")
    else:
        await ctx.send("Bot is already not running")
    await bot.logout()



### put discord token here
bot.run()
