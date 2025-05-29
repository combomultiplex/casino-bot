import discord
from discord.ext import commands
from discord import app_commands
import random
from datetime import timedelta
from utils import *
from config import Config

class Mining(commands.Cog):
    """Mining commands for the Discord bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="mine", description="Mine for resources")
    async def mine(self, interaction: discord.Interaction):
        """Mine command"""
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        if user.mining_energy < Config.MINING_ENERGY_COST:
            embed = create_error_embed(
                "Insufficient Energy", 
                f"You need {Config.MINING_ENERGY_COST} energy to mine!\nCurrent energy: {user.mining_energy}/100"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Deduct energy
        user.mining_energy -= Config.MINING_ENERGY_COST
        
        # Calculate mining rewards
        base_reward = Config.MINING_BASE_REWARD
        pickaxe_level = user.mining_data.get('pickaxe_level', 1)
        multiplier = user.get_boost_multiplier('mining')
        
        # Random bonus chance
        bonus_chance = random.random()
        if bonus_chance < 0.1:  # 10% chance for rare materials
            material = random.choice(['💎', '🏆', '⭐'])
            reward = int(base_reward * pickaxe_level * 3 * multiplier)
            reward_type = "rare"
        elif bonus_chance < 0.3:  # 20% chance for uncommon materials
            material = random.choice(['🥈', '🔶', '💰'])
            reward = int(base_reward * pickaxe_level * 2 * multiplier)
            reward_type = "uncommon"
        else:  # 70% chance for common materials
            material = random.choice(['🪨', '⚫', '🤎'])
            reward = int(base_reward * pickaxe_level * multiplier)
            reward_type = "common"
        
        # Give rewards
        user.balance += reward
        user.experience += 30
        
        # Update mining stats
        mining_data = user.mining_data
        mining_data['mined_today'] = mining_data.get('mined_today', 0) + 1
        mining_data['total_mined'] = mining_data.get('total_mined', 0) + reward
        
        # Add material to inventory
        user.add_item(material, 1)
        
        embed = create_embed("⛏️ Mining Result", color=EmbedColors.MINING)
        embed.add_field(name="Material Found", value=material, inline=True)
        embed.add_field(name="Rarity", value=reward_type.title(), inline=True)
        embed.add_field(name="Value", value=format_currency(reward, guild.cashmoji), inline=True)
        embed.add_field(name="Energy", value=f"{user.mining_energy}/100", inline=True)
        embed.add_field(name="Pickaxe Level", value=str(pickaxe_level), inline=True)
        
        if multiplier > 1:
            embed.add_field(name="Boost", value=f"{multiplier}x", inline=True)
        
        self.bot.data_manager.update_user(user)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="dig", description="Dig for buried treasure")
    async def dig(self, interaction: discord.Interaction):
        """Dig command - chance for special rewards"""
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        if user.is_on_cooldown('dig'):
            remaining = user.get_cooldown_remaining('dig')
            embed = create_error_embed(
                "Dig Cooldown", 
                f"You're tired from digging!\nNext dig in: {format_time_remaining(remaining)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if user.mining_energy < 20:
            embed = create_error_embed(
                "Insufficient Energy", 
                f"You need 20 energy to dig!\nCurrent energy: {user.mining_energy}/100"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Deduct energy and set cooldown
        user.mining_energy -= 20
        user.set_cooldown('dig', timedelta(minutes=30))
        
        # Dig results
        dig_chance = random.random()
        
        if dig_chance < 0.05:  # 5% chance for jackpot
            reward = random.randint(5000, 15000)
            item = "🏆"
            result = "legendary treasure chest"
            color = EmbedColors.SUCCESS
        elif dig_chance < 0.15:  # 10% chance for rare find
            reward = random.randint(1000, 3000)
            item = "💎"
            result = "rare gemstone"
            color = EmbedColors.ECONOMY
        elif dig_chance < 0.4:  # 25% chance for uncommon find
            reward = random.randint(300, 800)
            item = "🪙"
            result = "old coins"
            color = EmbedColors.WARNING
        elif dig_chance < 0.7:  # 30% chance for common find
            reward = random.randint(100, 300)
            item = "🔩"
            result = "scrap metal"
            color = EmbedColors.INFO
        else:  # 30% chance for nothing
            reward = 0
            item = "🪨"
            result = "just rocks and dirt"
            color = EmbedColors.ERROR
        
        if reward > 0:
            user.balance += reward
            user.add_item(item, 1)
            user.experience += 50
        
        embed = create_embed("🔍 Digging Result", color=color)
        embed.add_field(name="Found", value=f"{item} {result}", inline=False)
        
        if reward > 0:
            embed.add_field(name="Value", value=format_currency(reward, guild.cashmoji), inline=True)
        
        embed.add_field(name="Energy", value=f"{user.mining_energy}/100", inline=True)
        
        self.bot.data_manager.update_user(user)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="inventory", description="View your mining inventory")
    async def inventory(self, interaction: discord.Interaction):
        """Display mining inventory"""
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        
        embed = create_embed("📦 Mining Inventory", color=EmbedColors.MINING)
        
        inventory = user.inventory
        if not inventory:
            embed.add_field(name="Empty", value="No items in inventory", inline=False)
        else:
            # Group items by type
            materials = {}
            tools = {}
            treasures = {}
            
            for item, amount in inventory.items():
                if item in ['🪨', '⚫', '🤎', '🥈', '🔶', '💰', '💎', '🏆', '⭐']:
                    materials[item] = amount
                elif item in ['⛏️', '🔨', '🛠️']:
                    tools[item] = amount
                else:
                    treasures[item] = amount
            
            if materials:
                material_text = "\n".join([f"{item} x{amount}" for item, amount in materials.items()])
                embed.add_field(name="⛏️ Materials", value=material_text, inline=True)
            
            if tools:
                tool_text = "\n".join([f"{item} x{amount}" for item, amount in tools.items()])
                embed.add_field(name="🛠️ Tools", value=tool_text, inline=True)
            
            if treasures:
                treasure_text = "\n".join([f"{item} x{amount}" for item, amount in treasures.items()])
                embed.add_field(name="💰 Treasures", value=treasure_text, inline=True)
        
        # Mining stats
        mining_data = user.mining_data
        stats_text = f"""
Energy: {user.mining_energy}/100
Pickaxe Level: {mining_data.get('pickaxe_level', 1)}
Mined Today: {mining_data.get('mined_today', 0)}
Total Mined: {format_currency(mining_data.get('total_mined', 0), '⛏️')}
"""
        embed.add_field(name="📊 Mining Stats", value=stats_text, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="upgrade", description="Upgrade your mining equipment")
    @app_commands.describe(miner="Type of upgrade", upgrade_id="Specific upgrade", amount="Amount to upgrade")
    async def upgrade(self, interaction: discord.Interaction, 
                     miner: str = "pickaxe", 
                     upgrade_id: str = "level", 
                     amount: int = 1):
        """Upgrade mining equipment"""
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        if miner.lower() == "pickaxe" and upgrade_id.lower() == "level":
            current_level = user.mining_data.get('pickaxe_level', 1)
            
            # Calculate upgrade cost (exponential)
            base_cost = 1000
            total_cost = 0
            for i in range(amount):
                level_cost = base_cost * (2 ** (current_level + i - 1))
                total_cost += level_cost
            
            if user.balance < total_cost:
                embed = create_error_embed(
                    "Insufficient Funds", 
                    f"Upgrade cost: {format_currency(total_cost, guild.cashmoji)}\nYour balance: {format_currency(user.balance, guild.cashmoji)}"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Perform upgrade
            user.balance -= total_cost
            new_level = current_level + amount
            
            mining_data = user.mining_data
            mining_data['pickaxe_level'] = new_level
            
            embed = create_success_embed("⛏️ Pickaxe Upgraded!")
            embed.add_field(name="Previous Level", value=str(current_level), inline=True)
            embed.add_field(name="New Level", value=str(new_level), inline=True)
            embed.add_field(name="Cost", value=format_currency(total_cost, guild.cashmoji), inline=False)
            embed.add_field(name="Mining Efficiency", value=f"+{amount * 100}%", inline=True)
            
            self.bot.data_manager.update_user(user)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                embed=create_error_embed("Invalid Upgrade", "Currently only pickaxe level upgrades are available"), 
                ephemeral=True
            )
    
    @app_commands.command(name="process", description="Process raw materials into refined goods")
    async def process(self, interaction: discord.Interaction):
        """Process materials command"""
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        inventory = user.inventory
        
        # Check for materials to process
        raw_materials = ['🪨', '⚫', '🤎']
        total_raw = sum(inventory.get(material, 0) for material in raw_materials)
        
        if total_raw == 0:
            embed = create_error_embed(
                "No Materials", 
                "You don't have any raw materials to process!\nMine some materials first."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Process materials
        processed_value = 0
        processed_items = []
        
        for material in raw_materials:
            amount = inventory.get(material, 0)
            if amount > 0:
                # Remove raw materials
                user.remove_item(material, amount)
                
                # Add processed materials (50% chance for better material)
                for _ in range(amount):
                    if random.random() < 0.5:
                        processed_item = random.choice(['🥈', '🔶', '💰'])
                        value = 100
                    else:
                        processed_item = random.choice(['🔩', '⚡', '🔧'])
                        value = 50
                    
                    user.add_item(processed_item, 1)
                    processed_value += value
                    processed_items.append(processed_item)
        
        user.balance += processed_value
        user.experience += 75
        
        embed = create_success_embed("🔥 Materials Processed!")
        embed.add_field(name="Raw Materials Used", value=str(total_raw), inline=True)
        embed.add_field(name="Items Created", value=" ".join(processed_items[:10]), inline=True)
        embed.add_field(name="Value Added", value=format_currency(processed_value, guild.cashmoji), inline=False)
        
        self.bot.data_manager.update_user(user)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="start_mine", description="Start a mining expedition")
    async def start_mine(self, interaction: discord.Interaction):
        """Start mining expedition command"""
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        
        if user.is_on_cooldown('expedition'):
            remaining = user.get_cooldown_remaining('expedition')
            embed = create_error_embed(
                "Expedition in Progress", 
                f"Your miners are already working!\nExpedition completes in: {format_time_remaining(remaining)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Start expedition (2 hour duration)
        user.set_cooldown('expedition', timedelta(hours=2))
        
        embed = create_success_embed("⛏️ Mining Expedition Started!")
        embed.add_field(name="Duration", value="2 hours", inline=True)
        embed.add_field(name="Expected Rewards", value="Materials & Experience", inline=True)
        embed.add_field(name="Status", value="🟢 In Progress", inline=False)
        embed.add_field(name="Tip", value="Use `/mine` to collect resources while waiting!", inline=False)
        
        self.bot.data_manager.update_user(user)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Mining(bot))
