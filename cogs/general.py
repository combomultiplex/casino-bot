import discord
from discord.ext import commands
from modules.economy import Economy
from modules.helpers import make_embed
import os
import random
import bisect
from PIL import Image

from modules.helpers import ABS_PATH, InsufficientFundsException, DEFAULT_BET

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

    def check_bet(self, ctx: commands.Context, bet: int=DEFAULT_BET):
        bet = int(bet)
        if bet <= 0 or bet > 1000:
            raise commands.errors.BadArgument()
        current = self.economy.get_entry(ctx.author.id)[2]
        if bet > current:
            raise InsufficientFundsException(current, bet)

    @commands.command(
        brief='Slot machine\nbet must be 1-1000',
        usage='slots *[bet]'
    )
    async def slots(self, ctx: commands.Context, bet: int=1):
        self.check_bet(ctx, bet=bet)
        path = os.path.join(ABS_PATH, 'assets/')
        facade = Image.open(f'{path}slot-face.png').convert('RGBA')
        reel = Image.open(f'{path}slot-reel.png').convert('RGBA')

        rw, rh = reel.size
        item = 180
        items = rh//item

        s1 = random.randint(1, items-1)
        s2 = random.randint(1, items-1)
        s3 = random.randint(1, items-1)

        win_rate = 98/100

        if random.random() < win_rate:
            symbols_weights = [3.5, 7, 15, 25, 55] # 
            x = round(random.random()*100, 1)
            pos = bisect.bisect(symbols_weights, x)
            s1 = pos + (random.randint(1, int(items/6)-1) * 6)
            s2 = pos + (random.randint(1, int(items/6)-1) * 6)
            s3 = pos + (random.randint(1, int(items/6)-1) * 6)
            # ensure no reel hits the last symbol
            s1 = s1 - 6 if s1 == items else s1
            s2 = s2 - 6 if s2 == items else s2
            s3 = s3 - 6 if s3 == items else s3

        images = []
        speed = 6
        for i in range(1, (item//speed)+1):
            bg = Image.new('RGBA', facade.size, color=(255,255,255))
            bg.paste(reel, (25 + rw*0, 100-(speed * i * s1)))
            bg.paste(reel, (25 + rw*1, 100-(speed * i * s2))) # dont ask me why this works, but it took me hours
            bg.paste(reel, (25 + rw*2, 100-(speed * i * s3)))
            bg.alpha_composite(facade)
            images.append(bg)

        fp = str(id(ctx.author.id))+'.gif'
        images[0].save(
            fp,
            save_all=True,
            append_images=images[1:], # append all images after first to first
            duration=50  # duration of each slide (ms)
        )

        # win logic
        result = ('lost', bet)
        self.economy.add_credits(ctx.author.id, bet*-1)       
        # (1+s1)%6 gets the symbol 0-5 inclusive
        if (1+s1)%6 == (1+s2)%6 == (1+s3)%6:
            symbol = (1+s1)%6
            reward = [4, 80, 40, 25, 10, 5][symbol] * bet
            result = ('won', reward)
            self.economy.add_credits(ctx.author.id, reward)

        embed = make_embed(
            title=(
                f'You {result[0]} {result[1]} credits'+
                ('.' if result[0] == 'lost' else '!') # happy or sad based on outcome
            ),
            description=(
                'You now have ' +
                f'**{self.economy.get_entry(ctx.author.id)[2]}** ' +
                'credits.'
            ),
            color=(
                discord.Color.red() if result[0] == "lost"
                else discord.Color.green()
            )
        )

        file = discord.File(fp, filename=fp)
        embed.set_image(url=f"attachment://{fp}") # none of this makes sense to me :)
        await ctx.send(
            file=file,
            embed=embed
        )

async def setup(client: commands.Bot):
    await client.add_cog(GamblingHelpers(client))
