#!/usr/bin/env python3

# Vishnu by Valkyrie
#
# Discord bot that handles dice rolling and other things

import discord, yaml, vroll
from discord.ext import commands

config = yaml.safe_load(open("config.yaml"))
token = config['token']
chan_whitelist = config['chan_whitelist']

description = """
Vishnu, a multipurpose D&D bot.
"""

bot = commands.Bot(command_prefix='!', description=description)

@bot.command()
async def roll(ctx, *args):
    """
    Rolls dice. Accepts argumenuch as 1d6+4.
    """

    if chan_whitelist is None: # If the whitelist is empy, run the function in any channel
        for x in args:
            print("!roll command recieved in channel ID " + str(ctx.channel.id))
            await ctx.send(vroll.roll(x))


    elif ctx.channel.id in chan_whitelist: # Checks for the channel ID in the whitelist
        for x in args:
            print("!roll command recieved in channel ID " + str(ctx.channel.id) + " by user " + str(ctx.author))
            await ctx.send(vroll.roll(x))

@bot.event
async def on_ready():
    print("{0.user} connected to server".format(bot))
    print("Whitelisted channel IDs are: " + str(chan_whitelist))

bot.run(token)
