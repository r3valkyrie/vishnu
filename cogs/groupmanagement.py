import re
import texttable as tt
import yaml
import pgsql
import discord
from discord.ext import commands
from discord.utils import get
from inspect import cleandoc

config = yaml.safe_load(open("config.yaml"))
role_whitelist = " ".join(config['role_whitelist'])
chan_whitelist = config['chan_whitelist']
pg_connection = config['pg_connection']
group_category = config['group_category']


class GroupManagement(commands.Cog, name="Group Management Commands"):
    """
    Group management commands
    """

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    @commands.has_any_role(role_whitelist)
    async def groupadd(self, ctx, start_date, max_users, *notes):
        """
        Allows a DM to create a new group. Optionally add notes.

        Format dates like YYYY-MM-DD

        !groupadd [START DATE] [MAX USERS] [*NOTES]
        """

        creator = str(ctx.author)

        verify_message, group_id = pgsql.import_group_data(
            pg_connection,
            creator,
            start_date,
            max_users,
            " ".join(notes))

        await ctx.send(cleandoc(verify_message))

        new_role = "group-{}".format(str(group_id))

        await ctx.guild.create_role(
            name=new_role,
            mentionable=True,
            reason="Automated role creation, requested by {}"
            .format(str(ctx.author)))

        group_role = get(ctx.message.guild.roles, name=new_role)
        await ctx.author.add_roles(group_role)

        channel_overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(
                read_messages=False),
            ctx.guild.roles[ctx.guild.roles.index(group_role)]:
            discord.PermissionOverwrite(
                read_messages=True)
        }

        for category in ctx.guild.categories:
            if category.id == group_category:
                await ctx.guild.create_text_channel(
                    new_role + "-text",
                    category=category,
                    overwrites=channel_overwrites)

                await ctx.guild.create_voice_channel(
                    new_role + "-voice",
                    category=category,
                    overwrites=channel_overwrites)

    @commands.command()
    async def grouplist(self, ctx, *args):
        """
        Allows any user to list the groups available.

        !grouplist [id=ID] [creator=CREATOR]
        """

        command = " ".join(map(str, args))

        idsearch = r"id=([\d])"
        creatorsearch = r"creator=([^\s]+)"

        value_id = None
        value_creator = None

        if re.search(idsearch, command) is not None:
            value_id = re.search(idsearch, command).group(1)

        if re.search(creatorsearch, command) is not None:
            value_creator = re.search(creatorsearch, command).group(1)

        query_return = pgsql.retrieve_group_list(pg_connection,
                                                 value_id,
                                                 value_creator)

        # Format the results as a table
        tab = tt.Texttable()
        headings = ['ID', 'CREATOR', 'START DATE', 'MAX USERS', 'NOTES']
        tab.header(headings)

        for x in range(0, len(query_return), 5):
            for row in query_return[x:x+5]:
                tab.add_row(row)

            s = tab.draw()
            await ctx.send("```{}```".format(s))
            tab.reset()

    @commands.command()
    @commands.has_any_role(role_whitelist)
    async def test(ctx):
        await ctx.send(ctx.guild.categories)
        await ctx.send(group_category)


def setup(bot):
    bot.add_cog(GroupManagement(bot))
