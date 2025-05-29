import discord
from discord.ext import commands
from discord import app_commands
from utils import *

class Help(commands.Cog):
    """Help and utility commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="Get help with bot commands")
    @app_commands.describe(command_name="Specific command to get help for")
    async def help(self, interaction: discord.Interaction, command_name: str = None):
        """Help command"""
        if command_name:
            # Get help for specific command
            embed = await self.get_command_help(command_name)
        else:
            # General help
            embed = await self.get_general_help()
        
        await interaction.response.send_message(embed=embed)
    
    async def get_general_help(self) -> discord.Embed:
        """Get general help embed"""
        embed = create_embed("🎰 Casino & Mining Bot - Help", color=EmbedColors.INFO)
        
        embed.add_field(
            name="🎮 Games",
            value="`/blackjack` - Play blackjack\n`/coinflip` - Flip a coin\n`/slots` - Slot machine\n`/roulette` - Roulette wheel\n`/crash` - Crash game",
            inline=True
        )
        
        embed.add_field(
            name="💰 Economy", 
            value="`/profile` - View profile\n`/daily` - Daily reward\n`/weekly` - Weekly reward\n`/work` - Work for money\n`/send` - Send money",
            inline=True
        )
        
        embed.add_field(
            name="⛏️ Mining",
            value="`/mine` - Mine resources\n`/dig` - Dig for treasure\n`/inventory` - View inventory\n`/upgrade` - Upgrade equipment\n`/process` - Process materials",
            inline=True
        )
        
        embed.add_field(
            name="📊 Stats & Info",
            value="`/leaderboard` - View leaderboards\n`/cooldowns` - Check cooldowns\n`/stats` - Bot statistics",
            inline=True
        )
        
        embed.add_field(
            name="⚙️ Configuration",
            value="`/config` - Server settings\n`/invite` - Invite bot\n`/support` - Get support",
            inline=True
        )
        
        embed.add_field(
            name="🆘 Need More Help?",
            value="Use `/help <command>` for detailed command info\nJoin our support server with `/support`",
            inline=False
        )
        
        embed.set_footer(text="Tip: Most commands have optional parameters - explore them!")
        
        return embed
    
    async def get_command_help(self, command_name: str) -> discord.Embed:
        """Get help for specific command"""
        command_help = {
            'blackjack': {
                'description': 'Play a game of blackjack against the dealer',
                'usage': '/blackjack <bet> [mode]',
                'parameters': 'bet: Amount to wager\nmode: normal or insurance (optional)',
                'examples': '/blackjack 100\n/blackjack 500 insurance'
            },
            'coinflip': {
                'description': 'Flip a coin and bet on heads or tails',
                'usage': '/coinflip <prediction> <bet>',
                'parameters': 'prediction: heads or tails\nbet: Amount to wager',
                'examples': '/coinflip heads 250\n/coinflip tails 1000'
            },
            'slots': {
                'description': 'Play the slot machine for a chance to win big',
                'usage': '/slots <bet>',
                'parameters': 'bet: Amount to wager',
                'examples': '/slots 100\n/slots 500'
            },
            'roulette': {
                'description': 'Place bets on the roulette wheel',
                'usage': '/roulette <prediction> <bet>',
                'parameters': 'prediction: number (0-36), red, black, even, odd, low, high\nbet: Amount to wager',
                'examples': '/roulette red 200\n/roulette 17 100\n/roulette even 300'
            },
            'crash': {
                'description': 'Bet on a multiplier that increases until it crashes',
                'usage': '/crash <bet> [mode]',
                'parameters': 'bet: Amount to wager\nmode: manual or auto (optional)',
                'examples': '/crash 150\n/crash 300 auto'
            },
            'mine': {
                'description': 'Mine for valuable resources and materials',
                'usage': '/mine',
                'parameters': 'None - costs 10 energy per mine',
                'examples': '/mine'
            },
            'dig': {
                'description': 'Dig for buried treasure (30 minute cooldown)',
                'usage': '/dig',
                'parameters': 'None - costs 20 energy',
                'examples': '/dig'
            },
            'daily': {
                'description': 'Claim your daily reward (24 hour cooldown)',
                'usage': '/daily',
                'parameters': 'None',
                'examples': '/daily'
            },
            'work': {
                'description': 'Work various jobs to earn money (1 hour cooldown)',
                'usage': '/work',
                'parameters': 'None',
                'examples': '/work'
            },
            'profile': {
                'description': 'View your profile, stats, and inventory',
                'usage': '/profile [page]',
                'parameters': 'page: Profile page number (optional)',
                'examples': '/profile\n/profile 2'
            }
        }
        
        cmd = command_help.get(command_name.lower())
        if not cmd:
            return create_error_embed("Command Not Found", f"No help available for '{command_name}'")
        
        embed = create_embed(f"📖 Help: {command_name}", color=EmbedColors.INFO)
        embed.add_field(name="Description", value=cmd['description'], inline=False)
        embed.add_field(name="Usage", value=f"`{cmd['usage']}`", inline=False)
        embed.add_field(name="Parameters", value=cmd['parameters'], inline=False)
        embed.add_field(name="Examples", value=cmd['examples'], inline=False)
        
        return embed
    
    @app_commands.command(name="invite", description="Get the bot invite link")
    async def invite(self, interaction: discord.Interaction):
        """Bot invite command"""
        invite_link = f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=2147483647&scope=bot%20applications.commands"
        
        embed = create_embed("🤖 Invite Casino & Mining Bot", color=EmbedColors.SUCCESS)
        embed.add_field(
            name="Add to Your Server",
            value=f"[Click here to invite the bot]({invite_link})",
            inline=False
        )
        embed.add_field(
            name="Required Permissions",
            value="• Send Messages\n• Use Slash Commands\n• Embed Links\n• Add Reactions\n• Read Message History",
            inline=False
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="support", description="Get support and join our community")
    async def support(self, interaction: discord.Interaction):
        """Support command"""
        embed = create_embed("🆘 Support & Community", color=EmbedColors.INFO)
        embed.add_field(
            name="Need Help?",
            value="Having issues or questions? We're here to help!",
            inline=False
        )
        embed.add_field(
            name="Support Options",
            value="• Use `/help` for command information\n• Check our documentation\n• Report bugs to the developers",
            inline=False
        )
        embed.add_field(
            name="Community Features",
            value="• Regular tournaments\n• Feature updates\n• Community events\n• Bot announcements",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="stats", description="View bot statistics")
    async def stats(self, interaction: discord.Interaction):
        """Bot statistics command"""
        embed = create_embed("📊 Bot Statistics", color=EmbedColors.INFO)
        
        # Basic bot stats
        guild_count = len(self.bot.guilds)
        user_count = len(set(member.id for guild in self.bot.guilds for member in guild.members if not member.bot))
        
        embed.add_field(name="🏰 Servers", value=f"{guild_count:,}", inline=True)
        embed.add_field(name="👥 Users", value=f"{user_count:,}", inline=True)
        embed.add_field(name="📊 Commands", value=f"{len(self.bot.tree.get_commands()):,}", inline=True)
        
        # Data stats
        total_users = len(self.bot.data_manager.users)
        total_guilds = len(self.bot.data_manager.guilds)
        
        embed.add_field(name="💾 Registered Users", value=f"{total_users:,}", inline=True)
        embed.add_field(name="⚙️ Configured Servers", value=f"{total_guilds:,}", inline=True)
        embed.add_field(name="🎮 Active Games", value="0", inline=True)
        
        embed.set_footer(text=f"Bot latency: {round(self.bot.latency * 1000)}ms")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="delete_my_data", description="Delete all your data from the bot")
    async def delete_my_data(self, interaction: discord.Interaction):
        """Delete user data command"""
        view = DataDeletionConfirmView(self.bot, interaction.user.id)
        
        embed = create_embed("⚠️ Data Deletion", color=EmbedColors.WARNING)
        embed.add_field(
            name="Are you sure?",
            value="This will permanently delete ALL your data including:\n• Profile and balance\n• Game statistics\n• Mining progress\n• Inventory items\n• Achievement progress",
            inline=False
        )
        embed.add_field(
            name="⚠️ Warning",
            value="This action cannot be undone!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class DataDeletionConfirmView(discord.ui.View):
    """Confirmation view for data deletion"""
    
    def __init__(self, bot, user_id):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
    
    @discord.ui.button(label="Delete My Data", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return
        
        # Delete user data from all guilds
        user_key = str(self.user_id)
        if user_key in self.bot.data_manager.users:
            del self.bot.data_manager.users[user_key]
            self.bot.data_manager.save_all()
        
        embed = create_success_embed("✅ Data Deleted")
        embed.add_field(
            name="Complete",
            value="Your data has been permanently deleted from our systems.",
            inline=False
        )
        
        self.clear_items()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return
        
        embed = create_embed("❌ Cancelled")
        embed.add_field(name="No Changes", value="Your data has not been deleted.", inline=False)
        
        self.clear_items()
        await interaction.response.edit_message(embed=embed, view=self)

async def setup(bot):
    await bot.add_cog(Help(bot))
