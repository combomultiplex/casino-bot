import discord
from discord.ext import commands
from discord import app_commands
import random
from datetime import datetime, timedelta
from utils import *
from config import Config

class Economy(commands.Cog):
    """Economy commands for the Discord bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="profile", description="View your profile")
    @app_commands.describe(page="Profile page to view")
    async def profile(self, interaction: discord.Interaction, page: int = 1):
        """Display user profile"""
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        embed = create_embed(f"👤 {interaction.user.display_name}'s Profile", color=EmbedColors.INFO)
        
        if page == 1:
            # Main profile page
            embed.add_field(
                name="💰 Economy", 
                value=f"{guild.cashmoji} {user.balance:,}\n{guild.cryptomoji} {user.crypto_balance:,}", 
                inline=True
            )
            embed.add_field(
                name="📊 Level", 
                value=f"Level {user.level}\nXP: {user.experience:,}", 
                inline=True
            )
            embed.add_field(
                name="⚡ Mining Energy", 
                value=f"{user.mining_energy}/100\n{create_progress_bar(user.mining_energy, 100)}", 
                inline=True
            )
            
            stats = user.stats
            embed.add_field(
                name="🎮 Game Stats", 
                value=f"Played: {stats.get('games_played', 0)}\nWon: {stats.get('games_won', 0)}\nWin Rate: {(stats.get('games_won', 0) / max(stats.get('games_played', 1), 1) * 100):.1f}%", 
                inline=True
            )
            embed.add_field(
                name="💸 Betting Stats", 
                value=f"Total Bet: {format_currency(stats.get('total_bet', 0), guild.cashmoji)}\nTotal Won: {format_currency(stats.get('total_won', 0), guild.cashmoji)}", 
                inline=True
            )
        elif page == 2:
            # Inventory page
            inventory = user.inventory
            if not inventory:
                embed.add_field(name="📦 Inventory", value="Empty", inline=False)
            else:
                inv_text = ""
                for item, amount in inventory.items():
                    inv_text += f"{item}: {amount}\n"
                embed.add_field(name="📦 Inventory", value=inv_text[:1024], inline=False)
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="daily", description="Claim your daily reward")
    async def daily(self, interaction: discord.Interaction):
        """Daily reward command"""
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        # Check cooldown
        if user.is_on_cooldown('daily'):
            remaining = user.get_cooldown_remaining('daily')
            embed = create_error_embed(
                "Daily Reward", 
                f"You already claimed your daily reward!\nNext claim in: {format_time_remaining(remaining)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Calculate reward with boosts
        base_reward = Config.DAILY_REWARD
        multiplier = user.get_boost_multiplier('money')
        reward = int(base_reward * multiplier)
        
        # Give reward
        user.balance += reward
        user.experience += 50
        user.set_cooldown('daily', timedelta(seconds=Config.DAILY_COOLDOWN))
        
        embed = create_success_embed("💰 Daily Reward Claimed!")
        embed.add_field(name="Reward", value=format_currency(reward, guild.cashmoji), inline=True)
        if multiplier > 1:
            embed.add_field(name="Multiplier", value=f"{multiplier}x", inline=True)
        embed.add_field(name="Next Claim", value="24 hours", inline=True)
        
        self.bot.data_manager.update_user(user)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="weekly", description="Claim your weekly reward")
    async def weekly(self, interaction: discord.Interaction):
        """Weekly reward command"""
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        if user.is_on_cooldown('weekly'):
            remaining = user.get_cooldown_remaining('weekly')
            embed = create_error_embed(
                "Weekly Reward", 
                f"You already claimed your weekly reward!\nNext claim in: {format_time_remaining(remaining)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        base_reward = Config.WEEKLY_REWARD
        multiplier = user.get_boost_multiplier('money')
        reward = int(base_reward * multiplier)
        
        user.balance += reward
        user.experience += 200
        user.set_cooldown('weekly', timedelta(seconds=Config.WEEKLY_COOLDOWN))
        
        embed = create_success_embed("🎁 Weekly Reward Claimed!")
        embed.add_field(name="Reward", value=format_currency(reward, guild.cashmoji), inline=True)
        if multiplier > 1:
            embed.add_field(name="Multiplier", value=f"{multiplier}x", inline=True)
        
        self.bot.data_manager.update_user(user)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="monthly", description="Claim your monthly reward")
    async def monthly(self, interaction: discord.Interaction):
        """Monthly reward command"""
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        if user.is_on_cooldown('monthly'):
            remaining = user.get_cooldown_remaining('monthly')
            embed = create_error_embed(
                "Monthly Reward", 
                f"You already claimed your monthly reward!\nNext claim in: {format_time_remaining(remaining)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        base_reward = Config.MONTHLY_REWARD
        multiplier = user.get_boost_multiplier('money')
        reward = int(base_reward * multiplier)
        
        user.balance += reward
        user.crypto_balance += 50
        user.experience += 500
        user.set_cooldown('monthly', timedelta(seconds=Config.MONTHLY_COOLDOWN))
        
        embed = create_success_embed("🏆 Monthly Reward Claimed!")
        embed.add_field(name="Cash Reward", value=format_currency(reward, guild.cashmoji), inline=True)
        embed.add_field(name="Crypto Bonus", value=format_currency(50, guild.cryptomoji), inline=True)
        if multiplier > 1:
            embed.add_field(name="Multiplier", value=f"{multiplier}x", inline=True)
        
        self.bot.data_manager.update_user(user)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="work", description="Work to earn money")
    async def work(self, interaction: discord.Interaction):
        """Work command"""
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        if user.is_on_cooldown('work'):
            remaining = user.get_cooldown_remaining('work')
            embed = create_error_embed(
                "Work Cooldown", 
                f"You're tired from working!\nNext work available in: {format_time_remaining(remaining)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Random work scenarios
        jobs = [
            ("delivered pizzas", "🍕"),
            ("walked dogs", "🐕"),
            ("cleaned offices", "🧹"),
            ("did freelance coding", "💻"),
            ("sold handmade crafts", "🎨"),
            ("tutored students", "📚"),
            ("drove for rideshare", "🚗"),
            ("did yard work", "🌿")
        ]
        
        job, emoji = random.choice(jobs)
        base_reward = random.randint(Config.WORK_MIN_REWARD, Config.WORK_MAX_REWARD)
        multiplier = user.get_boost_multiplier('money')
        reward = int(base_reward * multiplier)
        
        user.balance += reward
        user.experience += 25
        user.set_cooldown('work', timedelta(seconds=Config.WORK_COOLDOWN))
        
        embed = create_success_embed(f"{emoji} Work Complete!")
        embed.add_field(name="Job", value=f"You {job}", inline=False)
        embed.add_field(name="Earned", value=format_currency(reward, guild.cashmoji), inline=True)
        if multiplier > 1:
            embed.add_field(name="Multiplier", value=f"{multiplier}x", inline=True)
        
        self.bot.data_manager.update_user(user)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="overtime", description="Work overtime for bonus pay")
    async def overtime(self, interaction: discord.Interaction):
        """Overtime work command"""
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        if user.is_on_cooldown('overtime'):
            remaining = user.get_cooldown_remaining('overtime')
            embed = create_error_embed(
                "Overtime Cooldown", 
                f"You're exhausted from overtime!\nNext overtime available in: {format_time_remaining(remaining)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        base_reward = random.randint(Config.WORK_MIN_REWARD, Config.WORK_MAX_REWARD)
        overtime_reward = int(base_reward * Config.OVERTIME_MULTIPLIER)
        multiplier = user.get_boost_multiplier('money')
        final_reward = int(overtime_reward * multiplier)
        
        user.balance += final_reward
        user.experience += 75
        user.set_cooldown('overtime', timedelta(seconds=Config.OVERTIME_COOLDOWN))
        
        embed = create_success_embed("⏰ Overtime Complete!")
        embed.add_field(name="Base Pay", value=format_currency(base_reward, guild.cashmoji), inline=True)
        embed.add_field(name="Overtime Bonus", value=f"{Config.OVERTIME_MULTIPLIER}x", inline=True)
        embed.add_field(name="Total Earned", value=format_currency(final_reward, guild.cashmoji), inline=False)
        
        self.bot.data_manager.update_user(user)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="send", description="Send money to another user")
    @app_commands.describe(recipient="User to send money to", amount="Amount to send")
    async def send(self, interaction: discord.Interaction, recipient: discord.Member, amount: int):
        """Send money to another user"""
        if recipient.bot:
            await interaction.response.send_message(
                embed=create_error_embed("Invalid Recipient", "You cannot send money to bots"), 
                ephemeral=True
            )
            return
        
        if recipient.id == interaction.user.id:
            await interaction.response.send_message(
                embed=create_error_embed("Invalid Recipient", "You cannot send money to yourself"), 
                ephemeral=True
            )
            return
        
        if amount <= 0:
            await interaction.response.send_message(
                embed=create_error_embed("Invalid Amount", "Amount must be positive"), 
                ephemeral=True
            )
            return
        
        sender = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        receiver = self.bot.data_manager.get_user(recipient.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        if sender.balance < amount:
            await interaction.response.send_message(
                embed=create_error_embed("Insufficient Balance", "You don't have enough money"), 
                ephemeral=True
            )
            return
        
        # Transfer money
        sender.balance -= amount
        receiver.balance += amount
        
        embed = create_success_embed("💸 Money Sent!")
        embed.add_field(name="From", value=interaction.user.mention, inline=True)
        embed.add_field(name="To", value=recipient.mention, inline=True)
        embed.add_field(name="Amount", value=format_currency(amount, guild.cashmoji), inline=False)
        
        self.bot.data_manager.update_user(sender)
        self.bot.data_manager.update_user(receiver)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard", description="View leaderboards")
    @app_commands.describe(
        leaderboard="Type of leaderboard", 
        category="Specific category", 
        global_scope="Show global leaderboard"
    )
    async def leaderboard(self, interaction: discord.Interaction, 
                         leaderboard: str = "player", 
                         category: str = "balance", 
                         global_scope: bool = False):
        """Display leaderboards"""
        guild_id = None if global_scope else interaction.guild.id
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        if leaderboard == "player":
            valid_categories = ["balance", "crypto", "level", "games_won"]
            if category not in valid_categories:
                await interaction.response.send_message(
                    embed=create_error_embed("Invalid Category", f"Valid categories: {', '.join(valid_categories)}"), 
                    ephemeral=True
                )
                return
            
            top_users = self.bot.data_manager.get_leaderboard(guild_id or interaction.guild.id, category, 10)
            
            embed = create_embed(f"🏆 {category.title()} Leaderboard", color=EmbedColors.ECONOMY)
            
            if not top_users:
                embed.add_field(name="No Data", value="No users found", inline=False)
            else:
                leaderboard_text = ""
                for i, user_data in enumerate(top_users, 1):
                    try:
                        user = self.bot.get_user(user_data['user_id'])
                        name = user.display_name if user else f"User {user_data['user_id']}"
                        
                        if category in ["balance", "crypto"]:
                            emoji = guild.cashmoji if category == "balance" else guild.cryptomoji
                            value_str = format_currency(user_data['value'], emoji)
                        else:
                            value_str = str(user_data['value'])
                        
                        medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
                        leaderboard_text += f"{medal} {name}: {value_str}\n"
                    except:
                        continue
                
                embed.add_field(name="Top Users", value=leaderboard_text[:1024], inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="cooldowns", description="Check your cooldowns")
    @app_commands.describe(detailed="Show detailed cooldown information")
    async def cooldowns(self, interaction: discord.Interaction, detailed: bool = False):
        """Display user cooldowns"""
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        
        embed = create_embed("⏰ Your Cooldowns", color=EmbedColors.INFO)
        
        cooldown_types = ['daily', 'weekly', 'monthly', 'work', 'overtime', 'mining']
        cooldown_text = ""
        
        for cooldown_type in cooldown_types:
            if user.is_on_cooldown(cooldown_type):
                remaining = user.get_cooldown_remaining(cooldown_type)
                cooldown_text += f"❌ **{cooldown_type.title()}**: {format_time_remaining(remaining)}\n"
            else:
                cooldown_text += f"✅ **{cooldown_type.title()}**: Ready!\n"
        
        embed.add_field(name="Status", value=cooldown_text, inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
