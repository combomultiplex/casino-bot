import discord
from discord.ext import commands
from modules.economy import Economy
from modules.helpers import make_embed

DEFAULT_BET = 100
B_MULT = 10
B_COOLDOWN = 24  # hours

class GamblingHelpers(commands.Cog, name='General'):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.economy = Economy()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def set(
        self,
        ctx: commands.Context,
        user_id: int=None,
        money: int=0,
        credits: int=0
    ):
        if money:
            self.economy.set_money(user_id, money, ctx.guild.id if ctx.guild else 0)
        if credits:
            self.economy.set_credits(user_id, credits, ctx.guild.id if ctx.guild else 0)
        await ctx.send("Set complete.")

    @commands.command(
        brief=f"Gives you ${DEFAULT_BET*B_MULT} once every {B_COOLDOWN}hrs",
        usage="add"
    )
    @commands.cooldown(1, B_COOLDOWN*3600, type=commands.BucketType.user)
    async def add(self, ctx: commands.Context):
        amount = DEFAULT_BET*B_MULT
        self.economy.add_money(ctx.author.id, amount, ctx.guild.id if ctx.guild else 0)
        await ctx.send(f"Added ${amount} come back in {B_COOLDOWN}hrs")

    @commands.command(
        brief="How much money you or someone else has",
        usage="money *[@member]",
        aliases=['credits']
    )
    async def money(self, ctx: commands.Context, user: discord.Member=None):
        user_obj = user or ctx.author
        profile = self.economy.get_entry(user_obj.id, ctx.guild.id if ctx.guild else 0)
        embed = make_embed(
            title=user_obj.display_name,
            description=(
                '**${:,}**'.format(profile[1]) +
                '\n**{:,}** credits'.format(profile[2])
            ),
            footer=None
        )
        embed.set_thumbnail(url=user_obj.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(
        brief="Shows the user with the most money",
        usage="leaderboard",
        aliases=["top"]
    )
    async def leaderboard(self, ctx):
        entries = self.economy.top_entries(5, ctx.guild.id if ctx.guild else 0)
        embed = make_embed(title='Leaderboard:', color=discord.Color.gold())
        for i, entry in enumerate(entries):
            user = self.client.get_user(entry[0]) or await self.client.fetch_user(entry[0])
            name = user.display_name if hasattr(user, "display_name") else user.name
            embed.add_field(
                name=f"{i+1}. {name}",
                value='${:,}'.format(entry[1]),
                inline=False
            )
        await ctx.send(embed=embed)

async def setup(client: commands.Bot):
    await client.add_cog(GamblingHelpers(client))
