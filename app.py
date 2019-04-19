#!/usr/bin/env python3
"""
Vishnu by Valkyrie
Discord bot that handles dice rolling and other things
"""

import yaml
import pgsql
import sys
import traceback
from discord.ext import commands

config = yaml.safe_load(open("config.yaml"))
token = config['token']
chan_whitelist = config['chan_whitelist']
pg_connection = config['pg_connection']
group_category = config['group-category']


# Create PostgreSQL tables.
pgsql.create_tables(pg_connection)

description = """
Vishnu, a multipurpose D&D bot.
"""


extensions = ['cogs.groupmanagement',
              'cogs.questmanagement']

bot = commands.Bot(command_prefix='!', description=description)

if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

bot.run(token, bot=True, reconnect=True)
