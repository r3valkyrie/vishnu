#!/usr/bin/env python3

# Vishnu by Valkyrie
#
# Discord bot that handles dice rolling and other things

import discord, yaml, vroll
from discord.ext import commands

config = yaml.safe_load(open("config.yaml"))
token = config['token']

bot = commands.Bot(command_prefix='!')

@bot.command()
async def roll(ctx, *args):
    for x in args:
        await ctx.send(vroll.roll(x))

@bot.event
async def on_ready():
    print("{0.user} connected to server".format(bot))

bot.run(token)
