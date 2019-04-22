import yaml
from discord.ext import commands

config = yaml.safe_load(open("config.yaml"))
role_whitelist = " ".join(config['role_whitelist'])
chan_whitelist = config['chan_whitelist']
pg_connection = config['pg_connection']
group_category = config['group_category']


class Debug(commands.Cog, name="Debug"):
    """
    Debugging Commands
    """

    def __init(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    @commands.has_any_role(role_whitelist)
    async def test(self, ctx):
        """
        Tests various things
        """
        await ctx.send(ctx.guild.categories)
        await ctx.send(group_category)


def setup(bot):
    bot.add_cog(Debug(bot))
