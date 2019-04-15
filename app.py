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
role_whitelist = config['role_whitelist']

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
    for x in role_whitelist:
        if x in [y.id for y in ctx.message.author.roles]:

            quest_desc = " ".join(desc)
            creator = str(ctx.author)

            pgsql.import_quest_data(pg_connection, quest_tier, quest_desc, creator)

            print("Tier {} quest added by {}. Description: {}".format(quest_tier, str(ctx.author), quest_desc))
            await ctx.send("Tier {} quest added by {}. Description: {}".format(quest_tier, str(ctx.author), quest_desc))
        else:
            await ctx.send("You don't have permission to use this command.")

@bot.command()
async def delquest(ctx, quest_id):
    """
    Allows a DM to delete a quest by their ID.

    !delquest [ID]
    """

    for x in role_whitelist:
        if x in [y.id for y in ctx.message.author.roles]:

            pgsql.delete_quest(pg_connection, quest_id)
            await ctx.send("Quest with ID " + quest_id + " deleted.")
        else:
            await ctx.send("You don't have permission to use this command.")

@bot.command()
async def questcomplete(ctx, quest_id):
    """
    Allows a DM to set a quest to 'complete' by specifying a quest ID.

    !questcomplete [ID]
    """

    for x in role_whitelist:
        if x in [y.id for y in ctx.message.author.roles]:
            pgsql.complete_quest(pg_connection, quest_id, True)
        else:
            await ctx.send("You don't have permission to use this command")

@bot.command()
async def questuncomplete(ctx, quest_id):
    """
    Allows a DM to set a quest to 'uncomplete' by specifying a quest ID.

    !questuncomplete [ID]
    """

    for x in role_whitelist:
        if x in [y.id for y in ctx.message.author.roles]:
            pgsql.complete_quest(pg_connection, quest_id, False)
        else:
            await ctx.send("You don't have permission to use this command")

@bot.command()
async def getquestbyid(ctx, quest_id):
    """
    Allows any user to retrieve quests by their ID.

    !getquest [ID]
    """

    conditional = """
    WHERE id = {} AND completed = 'f';
    """.format(quest_id)

    query_return = pgsql.retrieve_quest_data(pg_connection, conditional)
    print(query_return)

    # Texttable tabs
    tab = tt.Texttable()
    headings = ['ID', 'TIER', 'CREATOR', 'DESCRIPTION']
    tab.header(headings)

    for row in query_return:
        tab.add_row(row)

    s = tab.draw()
    await ctx.send("```" + s + "```")


@bot.command()
async def getquestbytier(ctx, tier):
    """
    Allows any user to retrieve quests by their tier.

    !getquest [TIER]
    """
    conditional = """
    WHERE tier = {} AND completed = 'f';
    """.format(tier)

    query_return = pgsql.retrieve_quest_data(pg_connection, conditional)
    print(query_return)

    # Texttable tabs
    tab = tt.Texttable()
    headings = ['ID', 'TIER', 'CREATOR', 'DESCRIPTION']
    tab.header(headings)

    for row in query_return:
        tab.add_row(row)

    s = tab.draw()
    await ctx.send("```" + s + "```")

@bot.command()
async def getquestbycreator(ctx, creator):
    """
    Allows any user to retrieve quests by their creators.

    !getquest [CREATOR]
    """
    conditional = """
    WHERE creator = '{}' AND completed = 'f';
    """.format(creator)

    query_return = pgsql.retrieve_quest_data(pg_connection, conditional)
    print(query_return)

    # Texttable tabs
    tab = tt.Texttable()
    headings = ['ID', 'TIER', 'CREATOR', 'DESCRIPTION']
    tab.header(headings)

    for row in query_return:
        tab.add_row(row)

    s = tab.draw()
    await ctx.send("```" + s + "```")

@bot.command()
async def getallquests(ctx, *args):
    """
    Allows a user to retrieve all uncomplete quests.

    !allquests
    """

    conditional = """
    """
    query_return = pgsql.retrieve_all_quests(pg_connection)
    print(query_return[1][1])

    # Texttable tabs
    tab = tt.Texttable()
    headings = ['ID', 'TIER', 'CREATOR', 'DESCRIPTION']
    tab.header(headings)

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
    print("Whitelisted role IDs are: " + str(role_whitelist))

bot.run(token)
