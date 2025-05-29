import discord
import os

# Provide ABS_PATH for compatibility with legacy code
ABS_PATH = os.path.dirname(os.path.abspath(__file__))

def make_embed(title="", description="", color=discord.Color.blue(), footer=None):
    embed = discord.Embed(title=title, description=description, color=color)
    # Support for legacy code passing discord.Embed.Empty as footer
    if footer not in (None, discord.Embed.Empty):
        embed.set_footer(text=footer)
    return embed

# Provide PREFIX for compatibility with legacy code
PREFIX = "!"

# Dummy exception for compatibility
class InsufficientFundsException(Exception):
    pass
