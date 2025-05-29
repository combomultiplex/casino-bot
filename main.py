import discord
from discord.ext import commands
import asyncio
import logging
import os
from config import Config
from database import DataManager
from modules.usermodel import UserModel, GuildModel

from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)

class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.db_manager = DataManager()
        
        # Compatibility wrapper methods
        def get_user(user_id: int, guild_id: int):
            db_user = self.db_manager.get_user(user_id, guild_id)
            return UserModel(db_user, self.db_manager)
        
        def get_guild(guild_id: int):
            db_guild = self.db_manager.get_guild(guild_id)
            return GuildModel(db_guild, self.db_manager)
        
        def update_user(user_model):
            self.db_manager.update_user(user_model._db_user)
        
        def update_guild(guild_model):
            self.db_manager.update_guild(guild_model._db_guild)
        
        def get_leaderboard(guild_id: int, category: str, limit: int = 10):
            return self.db_manager.get_leaderboard(guild_id, category, limit)
        
        # Create data_manager compatibility object
        class DataManagerCompat:
            def __init__(self):
                pass
            
            def get_user(self, user_id: int, guild_id: int):
                return get_user(user_id, guild_id)
            
            def get_guild(self, guild_id: int):
                return get_guild(guild_id)
            
            def update_user(self, user_model):
                return update_user(user_model)
            
            def update_guild(self, guild_model):
                return update_guild(guild_model)
            
            def get_leaderboard(self, guild_id: int, category: str, limit: int = 10):
                return get_leaderboard(guild_id, category, limit)
            
            def initialize_user(self, user_id: int, guild_id: int):
                return get_user(user_id, guild_id)
            
            def initialize_guild(self, guild_id: int):
                return get_guild(guild_id)
            
            def start_auto_save(self):
                self.db_manager.start_auto_save()
            
            def save_all(self):
                pass  # PostgreSQL handles this automatically
        
        self.data_manager = DataManagerCompat()
        self.data_manager.db_manager = self.db_manager
        
    async def setup_hook(self):
        """Setup hook to load cogs and sync commands"""
        # Load all cogs
        cogs_to_load = [
            'cogs.games',
            'cogs.economy', 
            'cogs.mining',
            'cogs.help',
            'cogs.guildconfig'
        ]
        
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logging.info(f"Loaded {cog}")
            except Exception as e:
                logging.error(f"Failed to load {cog}: {e}")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logging.info(f"Synced {len(synced)} commands")
        except Exception as e:
            logging.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logging.info(f'{self.user} has connected to Discord!')
        logging.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Start auto-save task
        self.data_manager.start_auto_save()
        
        # Set bot presence
        await self.change_presence(
            activity=discord.Game("🎰casino slots"),
            status=discord.Status.online
        )
    
    async def on_guild_join(self, guild):
        """Initialize guild data when joining a new guild"""
        self.data_manager.initialize_guild(guild.id)
        logging.info(f"Joined guild: {guild.name} ({guild.id})")
    
    async def on_member_join(self, member):
        """Initialize user data when a new member joins"""
        if not member.bot:
            self.data_manager.initialize_user(member.id, member.guild.id)

def main():
    """Main function to run the bot"""
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        logging.error("DISCORD_BOT_TOKEN environment variable not set!")
        return
    
    bot = DiscordBot()
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        logging.error("Invalid Discord bot token!")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
