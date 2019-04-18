#!/usr/bin/env python3
"""
Vishnu by Valkyrie
Discord bot that handles dice rolling and other things
"""

import re
import texttable as tt
import yaml
import vroll
import pgsql
import discord
from discord.ext import commands
from inspect import cleandoc

config = yaml.safe_load(open("config.yaml"))
token = config['token']
chan_whitelist = config['chan_whitelist']
pg_connection = config['pg_connection']
role_whitelist = config['role_whitelist']
permission_error_message = config['permission_error_message']
quest_tier_whitelist = config['quest_tiers']

# Create PostgreSQL tables.
pgsql.create_tables(pg_connection)

description = """
Vishnu, a multipurpose D&D bot.
"""

bot = commands.Bot(command_prefix='!', description=description)

"""
Role whitelisting function
"""


def whitelist_check(ctx):
    for x in role_whitelist:
        if x in [y.id for y in ctx.message.author.roles]:
            return True
        else:
            return False


"""
Quest-managment functions
"""


@bot.command()
async def addquest(ctx, quest_tier, *desc):
    """
    Allows a DM to create a quest.

    !addquest [TIER] [DESCRIPTION]
    """

    if whitelist_check(ctx):
        if quest_tier in quest_tier_whitelist:
            if len(desc) < 100:
                quest_desc = " ".join(desc)
                creator = str(ctx.author)

                pgsql.import_quest_data(pg_connection,
                                        quest_tier,
                                        quest_desc,
                                        creator)

                print(cleandoc("""Tier {} quest added by {}.
                Description: {}""".format(quest_tier,
                                          str(ctx.author),
                                          quest_desc)))
                await ctx.send(cleandoc("""Tier {} quest added by {}.
                Description: {}""".format(quest_tier,
                                          str(ctx.author),
                                          quest_desc)))
            else:
                await ctx.send(cleandoc("""Error: Your description is too long.
                The maximum allowed characters is 100.
                You had: {}""".format(str(len(desc)))))
        else:
            await ctx.send(cleandoc("""
            Error: The quest tier you specified is invalid.
            The valid quest tiers are: {}.
            You specified: {}.
            """.format(", ".join(quest_tier_whitelist), quest_tier)))
    else:
        await ctx.send(permission_error_message)


@bot.command()
async def delquest(ctx, quest_id):
    """
    Allows a DM to delete a quest by their ID.

    !delquest [ID]
    """

    if whitelist_check(ctx):
        pgsql.delete_quest(pg_connection, quest_id)
        await ctx.send("Quest with ID " + quest_id + " deleted.")
    else:
        await ctx.send(permission_error_message)


@bot.command()
async def questcomplete(ctx, quest_id):
    """
    Allows a DM to set a quest to 'complete' by specifying a quest ID.

    !questcomplete [ID]
    """

    if whitelist_check(ctx):
        pgsql.complete_quest(pg_connection, quest_id, True)
    else:
        await ctx.send(permission_error_message)


@bot.command()
async def questuncomplete(ctx, quest_id):
    """
    Allows a DM to set a quest to 'uncomplete' by specifying a quest ID.

    !questuncomplete [ID]
    """

    if whitelist_check(ctx):
        pgsql.complete_quest(pg_connection, quest_id, False)
    else:
        await ctx.send("You don't have permission to use this command")


@bot.command()
async def getquest(ctx, *args):
    """
    Allows any user to retrieve quests by specifying an ID, tier, or creator.
    Otherwise, returns all quests.

    !getquest [id=ID] [tier=TIER] [creator=CREATOR]
    """

    command = " ".join(map(str, args))

    idsearch = r"id=([\d])"
    tiersearch = r"tier=([^\s]+)"
    creatorsearch = r"creator=([^\s]+)"
    value_id = None
    value_tier = None
    value_creator = None

    if re.search(idsearch, command) is not None:
        value_id = re.search(idsearch, command).group(1)

    if re.search(tiersearch, command) is not None:
        value_tier = re.search(tiersearch, command).group(1)

    if re.search(creatorsearch, command) is not None:
        value_creator = re.search(creatorsearch, command).group(1)

    query_return = pgsql.retrieve_quest_data(pg_connection,
                                             value_id,
                                             value_tier,
                                             value_creator)

    # Format the results as a table
    tab = tt.Texttable()
    headings = ['ID', 'TIER', 'CREATOR', 'DESCRIPTION']
    tab.header(headings)

    for x in range(0, len(query_return), 5):
        for row in query_return[x:x+5]:
            tab.add_row(row)

        s = tab.draw()
        await ctx.send("```" + s + "```")
        tab.reset()


"""
Group management commands
"""


@bot.command()
async def addgroup(ctx, start_date, end_date, *notes):
    """
    Allows a DM to create a new group. Optionally add notes.

    Format dates like YYYY-MM-DD

    !addsession [START DATE] [END DATE] [*NOTES]
    """
    if whitelist_check(ctx):

        creator = str(ctx.author)

        verify_message, group_id = pgsql.import_group_data(
            pg_connection,
            creator,
            start_date,
            end_date,
            " ".join(notes))

        await ctx.send(cleandoc(verify_message))

        new_role = "group-{}".format(str(group_id))

        await ctx.guild.create_role(
            name=new_role,
            mentionable=True,
            reason="Automated role creation, requested by {}"
            .format(str(ctx.author)))

        group_role = discord.utils.get(ctx.message.guild.roles, name=new_role)
        await ctx.author.add_roles(group_role)

    else:
        await ctx.send(permission_error_message)


"""
Dice commands
"""


@bot.command()
async def roll(ctx, *args):
    """
    Rolls dice.

    !roll [NUM]d[FACES]+[NUM]
    """

    # If the whitelist is empy, run the roll function in any channel
    if chan_whitelist is None:
        for x in args:
            print("!roll command recieved in channel ID {}"
                  .format(ctx.channel.id))
            await ctx.send(vroll.roll(x))

    # Checks for the channel ID in the whitelist
    elif ctx.channel.id in chan_whitelist:
        for x in args:
            print("!roll command recieved in channel ID {} by user {}"
                  .format(str(ctx.channel.id),
                          str(ctx.author)))
            await ctx.send(vroll.roll(x))


@bot.event
async def on_ready():
    print("{0.user} connected to server".format(bot))
    print("Whitelisted channel IDs are: " + str(chan_whitelist))
    print("Whitelisted role IDs are: " + str(role_whitelist))

bot.run(token)
