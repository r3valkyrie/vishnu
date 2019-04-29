import re
import texttable as tt
import yaml
import lib.pgsql as pgsql
from discord.ext import commands
from inspect import cleandoc

config = yaml.safe_load(open("config.yaml"))
role_whitelist = " ".join(config['role_whitelist'])
quest_tier_whitelist = config['quest_tiers']

pg = pgsql.pgSQLManagement()


class QuestManagement(commands.Cog, name="Quest Management Commands"):
    """
    Quest-managment functions
    """

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    @commands.has_any_role(role_whitelist)
    async def questadd(self, ctx, quest_tier, *desc):
        """
        Allows a DM to create a quest.

        !questadd [TIER] [DESCRIPTION]
        """

        if quest_tier in quest_tier_whitelist:
            if len(desc) < 100:
                quest_desc = " ".join(desc)
                creator = str(ctx.author)

                await pg.import_quest_data(
                                        quest_tier,
                                        quest_desc,
                                        creator)

                print(cleandoc("""Tier {} quest added by {}.
                Description: {}""".format(
                    quest_tier,
                    str(ctx.author),
                    quest_desc)))

                await ctx.send(cleandoc("""Tier {} quest added by {}.
                Description: {}""".format(
                    quest_tier,
                    str(ctx.author),
                    quest_desc)))
            else:
                await ctx.send(cleandoc("""Error: Your description is too long.
                The maximum allowed characters is 100.
                You had: {}""".format(
                    str(len(desc)))))
        else:
            await ctx.send(cleandoc("""
            Error: The quest tier you specified is invalid.
            The valid quest tiers are: {}.
            You specified: {}.
            """.format(", ".join(
                quest_tier_whitelist),
                       quest_tier)))

    @commands.command()
    @commands.has_any_role(role_whitelist)
    async def questdel(self, ctx, quest_id):
        """
        Allows a DM to delete a quest by their ID.

        !questdel [ID]
        """

        await pg.delete_quest(quest_id)
        await ctx.send("Quest with ID " + quest_id + " deleted.")

    @commands.command()
    @commands.has_any_role(role_whitelist)
    async def questcomplete(self, ctx, quest_id):
        """
        Allows a DM to set a quest to 'complete' by specifying a quest ID.

        !questcomplete [ID]
        """

        await pg.complete_quest(quest_id, True)

    @commands.command()
    @commands.has_any_role(role_whitelist)
    async def questuncomplete(self, ctx, quest_id):
        """
        Allows a DM to set a quest to 'uncomplete' by specifying a quest ID.

        !questuncomplete [ID]
        """

        await pg.complete_quest(quest_id, False)

    @commands.command()
    async def questlist(self, ctx, *args):
        """
        Allows any user to retrieve quests by specifying an
        ID, tier, or creator. Otherwise, returns all quests.

        !questlist [id=ID] [tier=TIER] [creator=CREATOR]
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

        query_return = await pg.retrieve_quest_data(
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
            await ctx.send("```{}```".format(s))
            tab.reset()


def setup(bot):
    bot.add_cog(QuestManagement(bot))
