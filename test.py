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
async def test(ctx, *args):
    """
    test
    """

    await ctx.send(ctx.author)

@bot.event
async def on_ready():
    print("{0.user} connected to server".format(bot))
    print("Whitelisted channel IDs are: " + str(chan_whitelist))

bot.run(token)
