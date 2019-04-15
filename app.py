#!/usr/bin/env python3

# Vishnu by Valkyrie
#
# Discord bot that handles dice rolling and other things

import discord, yaml, vroll, pgsql
import texttable as tt
from discord.ext import commands

config = yaml.safe_load(open("config.yaml"))
token = config['token']
chan_whitelist = config['chan_whitelist']
pg_connection = config['pg_connection']

# Create PostgreSQL tables.
pgsql.create_tables(pg_connection)

description = """
Vishnu, a multipurpose D&D bot.
"""

bot = commands.Bot(command_prefix='!', description=description)


"""
QUEST-RELATED COMMANDS
"""
@bot.command()
async def addquest(ctx, quest_tier, *desc):
    """
    Allows a DM to create a quest.

    !addquest [TIER] [DESCRIPTION]
    """
    quest_desc = " ".join(desc)
    creator = str(ctx.author)

    pgsql.import_quest_data(pg_connection, quest_tier, quest_desc, creator)

    print("Tier {} quest added by {}. Description: {}".format(quest_tier, str(ctx.author), quest_desc))
    await ctx.send("Tier {} quest added by {}. Description: {}".format(quest_tier, str(ctx.author), quest_desc))

@bot.command()
async def getquest(ctx, quest_id):
    """
    Allows any user to retrieve a quest by it's ID.

    !getquest [ID]
    """

    query_return = pgsql.retrieve_quest_data(pg_connection, quest_id)
    await ctx.send("""
    QUEST ID: {} \nTIER: {}\nDESCRIPTION {}\nCREATOR: {}
    {}
    """.format(query_return[0], query_return[1], query_return[2], query_return[3], '-' * 20))

@bot.command()
async def getallquests(ctx):
    """
    Allows a user to retrieve all available quests

    !allquests
    """
    tab = tt.Texttable()
    headings = ['ID', 'TIER', 'DESCRIPTION', 'CREATOR', 'COMPLETED']
    tab.header(headings)

    query_return = pgsql.retrieve_all_quests(pg_connection)
    print(query_return[1][1])

    for row in query_return:
        tab.add_row(row)

    s = tab.draw()
    await ctx.send("```" + s + "```")


"""
DICE COMMANDS
"""
@bot.command()
async def roll(ctx, *args):
    """
    Rolls dice.

    !roll [NUM]d[FACES]+[NUM]
    """

    if chan_whitelist is None: # If the whitelist is empy, run the roll function in any channel
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
