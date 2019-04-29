import re
import texttable as tt
import yaml
import lib.pgsql as pgsql
import discord
from discord.ext import commands
from discord.utils import get
from inspect import cleandoc

config = yaml.safe_load(open("config.yaml"))
role_whitelist = " ".join(config['role_whitelist'])
chan_whitelist = config['chan_whitelist']
group_category = config['group_category']
announce_chan = config['announce_chan']

pg = pgsql.pgSQLManagement()


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

        verify_message, group_id = await pg.import_group_data(
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

        group_role = None

        while group_role is None:
            try:
                group_role = get(ctx.message.guild.roles, name=new_role)
            except Exception:
                pass

            await ctx.author.add_roles(group_role)

        channel_overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(
                read_messages=False),
            ctx.guild.roles[ctx.guild.roles.index(group_role)]:
            discord.PermissionOverwrite(
                read_messages=True)
        }

        try:
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
        except Exception as e:
            print(e)

        finally:
            announce_channel = get(ctx.message.guild.channels,
                                   id=announce_chan)
            await announce_channel.send(cleandoc("""
            --------------------
            {} created a session on {} with a max player count of {}.
            Use `!groupjoin {}` to join this session.
            Additional notes: {}
            --------------------""".format(
                ctx.author,
                start_date,
                max_users,
                group_id,
                " ".join(notes))))

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

        query_return = await pg.retrieve_group_list(
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
    async def groupjoin(self, ctx, group_id):
        """
        Allows any user to join a group so long as it has users available.

        !groupjoin [ID]
        """
        ret_groupinfo = await pg.retrieve_group_info(
            group_id)
        print(ret_groupinfo)

        # session_id = ret_groupinfo[0][0]
        max_players = ret_groupinfo[0][1]
        session_members = ret_groupinfo[0][2]
        # session_owner = ret_groupinfo[0][3]

        regex_check = r"(^\d+)\/(\d+)$"

        matches = re.search(regex_check, max_players)

        print(matches.group(0), matches.group(1), matches.group(2))
        print(session_members)

        slots_taken = int(matches.group(1))
        slots_max = int(matches.group(2))

        if slots_taken < slots_max:
            if session_members is None or str(ctx.author) not in session_members:
                slots_taken += 1
                new_max = "{}/{}".format(slots_taken, slots_max)
                await pg.join_group(group_id, str(ctx.author), new_max)

                role = get(ctx.guild.roles, name="group-{}".format(group_id))
                await ctx.author.add_roles(role)

                await ctx.send("{} joined group with ID of {}!".format(
                    ctx.author,
                    group_id))
            else:
                await ctx.send("{} is already a member of this group!".format(
                    str(ctx.author)))
        else:
            await ctx.send("Group is already full! ({})".format(
                ret_groupinfo[0][1]))

    @commands.command()
    async def groupclose(self, ctx):
        """
        Allows a group owner to close a group.

        Run this in the group's channel.
        """

        text_channel = ctx.message.channel

        channel_regex = r"^group-(\d+)-"
        matches = re.search(channel_regex, str(text_channel))

        group_id = matches.group(1)
        voice_channel_name = "group-{}-voice".format(group_id)
        role_name = "group-{}".format(group_id)

        voice_channel = get(ctx.guild.voice_channels, name=voice_channel_name)
        role = get(ctx.guild.roles, name=role_name)

        query_return = await pg.retrieve_group_info(group_id)
        for row in query_return:
            if str(ctx.author) == str(row[3]):
                await role.delete(reason="Group has been closed.")
                await voice_channel.delete(reason="Group has been closed.")
                await text_channel.delete(reason="Group has been closed.")

                await pg.delete_group(group_id)
            else:
                await ctx.send("You are not the owner of this group!")


def setup(bot):
    bot.add_cog(GroupManagement(bot))
