import discord
from discord.ext import commands
from discord import app_commands
from modules.utils import *
from config import Config

class GuildConfig(commands.Cog):
    """Guild configuration commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    def is_admin_or_owner(self, interaction: discord.Interaction) -> bool:
        """Check if user is admin or server owner"""
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        return (interaction.user.guild_permissions.administrator or 
                interaction.user.id == interaction.guild.owner_id or
                guild.is_admin(interaction.user.id))
    
    @app_commands.command(name="config", description="Configure server settings")
    @app_commands.describe(action="Configuration action to perform")
    async def config(self, interaction: discord.Interaction, action: str = "show"):
        """Main configuration command"""
        if action.lower() == "show":
            await self.show_config(interaction)
        else:
            await interaction.response.send_message(
                embed=create_error_embed("Invalid Action", "Use 'show' to view current configuration"), 
                ephemeral=True
            )
    
    async def show_config(self, interaction: discord.Interaction):
        """Show current guild configuration"""
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        embed = create_embed(f"⚙️ {interaction.guild.name} Configuration", color=EmbedColors.INFO)
        
        # Currency settings
        embed.add_field(
            name="💰 Currency Settings",
            value=f"Cash Name: {guild.cash_name}\nCash Emoji: {guild.cashmoji}\nCrypto Name: {guild.crypto_name}\nCrypto Emoji: {guild.cryptomoji}",
            inline=True
        )
        
        # Channel settings
        channels_text = "All channels" if not guild.channels else f"{len(guild.channels)} specific channels"
        embed.add_field(
            name="📢 Allowed Channels",
            value=channels_text,
            inline=True
        )
        
        # Admin settings
        admin_count = len(guild.admin_ids)
        embed.add_field(
            name="👑 Bot Admins",
            value=f"{admin_count} admins configured",
            inline=True
        )
        
        # Other settings
        embed.add_field(
            name="🔔 Update Messages",
            value="Disabled" if guild.disable_update_messages else "Enabled",
            inline=True
        )
        
        # Configuration commands help
        embed.add_field(
            name="📖 Configuration Commands",
            value="`/config_cash_name` - Set cash currency name\n`/config_cashmoji` - Set cash emoji\n`/config_crypto_name` - Set crypto currency name\n`/config_cryptomoji` - Set crypto emoji\n`/config_channels` - Set allowed channels\n`/config_admins` - Manage bot admins",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="config_cash_name", description="Set the cash currency name")
    @app_commands.describe(name="New name for cash currency")
    async def config_cash_name(self, interaction: discord.Interaction, name: str):
        """Configure cash currency name"""
        if not self.is_admin_or_owner(interaction):
            await interaction.response.send_message(
                embed=create_error_embed("Permission Denied", "You need administrator permissions or be a bot admin"), 
                ephemeral=True
            )
            return
        
        if len(name) > 20:
            await interaction.response.send_message(
                embed=create_error_embed("Invalid Name", "Currency name must be 20 characters or less"), 
                ephemeral=True
            )
            return
        
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        old_name = guild.cash_name
        guild.cash_name = name
        
        embed = create_success_embed("💰 Cash Name Updated")
        embed.add_field(name="Previous", value=old_name, inline=True)
        embed.add_field(name="New", value=name, inline=True)
        
        self.bot.data_manager.update_guild(guild)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="config_cashmoji", description="Set the cash currency emoji")
    @app_commands.describe(emoji="New emoji for cash currency")
    async def config_cashmoji(self, interaction: discord.Interaction, emoji: str):
        """Configure cash currency emoji"""
        if not self.is_admin_or_owner(interaction):
            await interaction.response.send_message(
                embed=create_error_embed("Permission Denied", "You need administrator permissions or be a bot admin"), 
                ephemeral=True
            )
            return
        
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        old_emoji = guild.cashmoji
        guild.cashmoji = emoji
        
        embed = create_success_embed("💰 Cash Emoji Updated")
        embed.add_field(name="Previous", value=old_emoji, inline=True)
        embed.add_field(name="New", value=emoji, inline=True)
        
        self.bot.data_manager.update_guild(guild)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="config_crypto_name", description="Set the crypto currency name")
    @app_commands.describe(name="New name for crypto currency")
    async def config_crypto_name(self, interaction: discord.Interaction, name: str):
        """Configure crypto currency name"""
        if not self.is_admin_or_owner(interaction):
            await interaction.response.send_message(
                embed=create_error_embed("Permission Denied", "You need administrator permissions or be a bot admin"), 
                ephemeral=True
            )
            return
        
        if len(name) > 20:
            await interaction.response.send_message(
                embed=create_error_embed("Invalid Name", "Currency name must be 20 characters or less"), 
                ephemeral=True
            )
            return
        
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        old_name = guild.crypto_name
        guild.crypto_name = name
        
        embed = create_success_embed("💎 Crypto Name Updated")
        embed.add_field(name="Previous", value=old_name, inline=True)
        embed.add_field(name="New", value=name, inline=True)
        
        self.bot.data_manager.update_guild(guild)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="config_cryptomoji", description="Set the crypto currency emoji")
    @app_commands.describe(emoji="New emoji for crypto currency")
    async def config_cryptomoji(self, interaction: discord.Interaction, emoji: str):
        """Configure crypto currency emoji"""
        if not self.is_admin_or_owner(interaction):
            await interaction.response.send_message(
                embed=create_error_embed("Permission Denied", "You need administrator permissions or be a bot admin"), 
                ephemeral=True
            )
            return
        
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        old_emoji = guild.cryptomoji
        guild.cryptomoji = emoji
        
        embed = create_success_embed("💎 Crypto Emoji Updated")
        embed.add_field(name="Previous", value=old_emoji, inline=True)
        embed.add_field(name="New", value=emoji, inline=True)
        
        self.bot.data_manager.update_guild(guild)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="config_channels", description="Set allowed channels for bot commands")
    @app_commands.describe(
        channel1="First allowed channel",
        channel2="Second allowed channel",
        channel3="Third allowed channel",
        channel4="Fourth allowed channel",
        channel5="Fifth allowed channel"
    )
    async def config_channels(self, interaction: discord.Interaction, 
                            channel1: discord.TextChannel = None,
                            channel2: discord.TextChannel = None,
                            channel3: discord.TextChannel = None,
                            channel4: discord.TextChannel = None,
                            channel5: discord.TextChannel = None):
        """Configure allowed channels"""
        if not self.is_admin_or_owner(interaction):
            await interaction.response.send_message(
                embed=create_error_embed("Permission Denied", "You need administrator permissions or be a bot admin"), 
                ephemeral=True
            )
            return
        
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        # Collect non-None channels
        channels = [ch for ch in [channel1, channel2, channel3, channel4, channel5] if ch is not None]
        channel_ids = [ch.id for ch in channels]
        
        guild.set_channels(channel_ids)
        
        embed = create_success_embed("📢 Allowed Channels Updated")
        
        if channels:
            channel_mentions = "\n".join([ch.mention for ch in channels])
            embed.add_field(name="Allowed Channels", value=channel_mentions, inline=False)
        else:
            embed.add_field(name="Allowed Channels", value="All channels (no restrictions)", inline=False)
        
        self.bot.data_manager.update_guild(guild)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="config_add_admin", description="Add a bot admin")
    @app_commands.describe(user="User to add as bot admin")
    async def config_add_admin(self, interaction: discord.Interaction, user: discord.Member):
        """Add bot admin"""
        if not self.is_admin_or_owner(interaction):
            await interaction.response.send_message(
                embed=create_error_embed("Permission Denied", "You need administrator permissions or be a bot admin"), 
                ephemeral=True
            )
            return
        
        if user.bot:
            await interaction.response.send_message(
                embed=create_error_embed("Invalid User", "Cannot add bots as admins"), 
                ephemeral=True
            )
            return
        
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        if guild.is_admin(user.id):
            await interaction.response.send_message(
                embed=create_error_embed("Already Admin", f"{user.mention} is already a bot admin"), 
                ephemeral=True
            )
            return
        
        guild.add_admin(user.id)
        
        embed = create_success_embed("👑 Bot Admin Added")
        embed.add_field(name="New Admin", value=user.mention, inline=True)
        embed.add_field(name="Total Admins", value=str(len(guild.admin_ids)), inline=True)
        
        self.bot.data_manager.update_guild(guild)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="config_remove_admin", description="Remove a bot admin")
    @app_commands.describe(user="User to remove from bot admins")
    async def config_remove_admin(self, interaction: discord.Interaction, user: discord.Member):
        """Remove bot admin"""
        if not self.is_admin_or_owner(interaction):
            await interaction.response.send_message(
                embed=create_error_embed("Permission Denied", "You need administrator permissions or be a bot admin"), 
                ephemeral=True
            )
            return
        
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        if not guild.is_admin(user.id):
            await interaction.response.send_message(
                embed=create_error_embed("Not Admin", f"{user.mention} is not a bot admin"), 
                ephemeral=True
            )
            return
        
        guild.remove_admin(user.id)
        
        embed = create_success_embed("👑 Bot Admin Removed")
        embed.add_field(name="Removed Admin", value=user.mention, inline=True)
        embed.add_field(name="Remaining Admins", value=str(len(guild.admin_ids)), inline=True)
        
        self.bot.data_manager.update_guild(guild)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="config_disable_updates", description="Toggle update messages")
    @app_commands.describe(enabled="Whether to disable update messages")
    async def config_disable_updates(self, interaction: discord.Interaction, enabled: bool):
        """Configure update messages"""
        if not self.is_admin_or_owner(interaction):
            await interaction.response.send_message(
                embed=create_error_embed("Permission Denied", "You need administrator permissions or be a bot admin"), 
                ephemeral=True
            )
            return
        
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        guild.disable_update_messages = enabled
        
        status = "disabled" if enabled else "enabled"
        embed = create_success_embed("🔔 Update Messages Configuration")
        embed.add_field(name="Status", value=f"Update messages are now {status}", inline=False)
        
        self.bot.data_manager.update_guild(guild)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="updates", description="View recent bot updates")
    async def updates(self, interaction: discord.Interaction):
        """Show recent updates"""
        embed = create_embed("📢 Recent Updates", color=EmbedColors.INFO)
        
        # Mock update information - in a real bot this would come from a database or config
        updates_text = """
**Version 1.0.0** - Initial Release
• Complete gambling system with blackjack, slots, roulette, coinflip, and crash
• Full economy system with daily/weekly/monthly rewards
• Mining system with upgrades and processing
• Comprehensive profile and statistics tracking
• Guild configuration system
• Leaderboards and cooldown management

**Features:**
• Slash command integration
• In-memory data persistence
• Modular command structure
• Error handling and validation
• Boost system for enhanced rewards
"""
        
        embed.add_field(name="Latest Updates", value=updates_text, inline=False)
        embed.set_footer(text="More updates coming soon!")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(GuildConfig(bot))
