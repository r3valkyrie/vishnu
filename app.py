#!/usr/bin/env python3
"""
Vishnu by Valkyrie
Discord bot that handles dice rolling and other things
"""

import yaml
import modules.pgsql as pgsql
import traceback
from discord.ext import commands

config = yaml.safe_load(open("config.yaml"))
guild_id = config['guild_id']
token = config['token']
role_whitelist = " ".join(config['role_whitelist'])

description = """
Vishnu, a multipurpose D&D bot.
"""


extensions = ['cogs.groupmanagement',
              'cogs.questmanagement']

bot = commands.Bot(command_prefix='!', description=description)


@bot.command()
@commands.has_any_role(role_whitelist)
async def load(ctx, extension_name: str):
    """
    Loads an extension
    """
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))

    await ctx.send("{} loaded".format(extension_name))

if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(e)
            traceback.print_exc()


@bot.event
async def on_ready():
    # Create PostgreSQL tables.
    pg = pgsql.pgSQLManagement()
    await pg.create_tables()

    print(f"Logged in as {bot.user.name}")

bot.run(token, bot=True, reconnect=True)
