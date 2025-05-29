import json
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from models import User, Guild, GameState
from config import Config

class DataManager:
    """Manages all data persistence and user/guild operations"""
    
    def __init__(self):
        self.data_dir = "data"
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.guilds_file = os.path.join(self.data_dir, "guilds.json")
        self.game_states_file = os.path.join(self.data_dir, "gamestates.json")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data files if they don't exist
        self._initialize_files()
        
        # Load data into memory
        self.users = self._load_json(self.users_file, {})
        self.guilds = self._load_json(self.guilds_file, {})
        self.game_states = self._load_json(self.game_states_file, {})
        
        # Auto-save task will be started when bot is ready
        self._auto_save_task = None
    
    def start_auto_save(self):
        """Start the auto-save task"""
        if self._auto_save_task is None:
            self._auto_save_task = asyncio.create_task(self._auto_save())
    
    def _initialize_files(self):
        """Initialize JSON files if they don't exist"""
        for file_path in [self.users_file, self.guilds_file, self.game_states_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)
    
    def _load_json(self, file_path: str, default: Any = None) -> Any:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default or {}
    
    def _save_json(self, file_path: str, data: Any):
        """Save data to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logging.error(f"Error saving {file_path}: {e}")
    
    async def _auto_save(self):
        """Auto-save data every 5 minutes"""
        while True:
            await asyncio.sleep(300)  # 5 minutes
            self.save_all()
    
    def save_all(self):
        """Save all data to files"""
        self._save_json(self.users_file, self.users)
        self._save_json(self.guilds_file, self.guilds)
        self._save_json(self.game_states_file, self.game_states)
    
    def initialize_user(self, user_id: int, guild_id: int) -> User:
        """Initialize a new user or return existing user"""
        user_key = str(user_id)
        guild_key = str(guild_id)
        
        if user_key not in self.users:
            self.users[user_key] = {}
        
        if guild_key not in self.users[user_key]:
            self.users[user_key][guild_key] = {
                'balance': 1000,
                'crypto_balance': 0,
                'experience': 0,
                'level': 1,
                'inventory': {},
                'mining': {
                    'energy': Config.MINING_MAX_ENERGY,
                    'pickaxe_level': 1,
                    'mined_today': 0,
                    'total_mined': 0
                },
                'stats': {
                    'games_played': 0,
                    'games_won': 0,
                    'total_bet': 0,
                    'total_won': 0
                },
                'cooldowns': {},
                'boosts': {},
                'prestige': {
                    'money': 0,
                    'mining': 0,
                    'games': 0
                },
                'achievements': [],
                'last_seen': datetime.now().isoformat()
            }
        
        return User(self.users[user_key][guild_key], user_id, guild_id)
    
    def initialize_guild(self, guild_id: int) -> Guild:
        """Initialize a new guild or return existing guild"""
        guild_key = str(guild_id)
        
        if guild_key not in self.guilds:
            self.guilds[guild_key] = Config.DEFAULT_GUILD_CONFIG.copy()
        
        return Guild(self.guilds[guild_key], guild_id)
    
    def get_user(self, user_id: int, guild_id: int) -> User:
        """Get user data"""
        return self.initialize_user(user_id, guild_id)
    
    def get_guild(self, guild_id: int) -> Guild:
        """Get guild data"""
        return self.initialize_guild(guild_id)
    
    def update_user(self, user: User):
        """Update user data in memory"""
        user_key = str(user.user_id)
        guild_key = str(user.guild_id)
        
        if user_key not in self.users:
            self.users[user_key] = {}
        
        self.users[user_key][guild_key] = user.to_dict()
    
    def update_guild(self, guild: Guild):
        """Update guild data in memory"""
        guild_key = str(guild.guild_id)
        self.guilds[guild_key] = guild.to_dict()
    
    def get_leaderboard(self, guild_id: int, category: str, limit: int = 10) -> list:
        """Get leaderboard for a specific category"""
        guild_key = str(guild_id)
        leaderboard = []
        
        for user_id, user_guilds in self.users.items():
            if guild_key in user_guilds:
                user_data = user_guilds[guild_key]
                value = 0
                
                if category == 'balance':
                    value = user_data.get('balance', 0)
                elif category == 'crypto':
                    value = user_data.get('crypto_balance', 0)
                elif category == 'level':
                    value = user_data.get('level', 1)
                elif category == 'mining':
                    value = user_data.get('mining', {}).get('total_mined', 0)
                elif category == 'games_won':
                    value = user_data.get('stats', {}).get('games_won', 0)
                
                leaderboard.append({
                    'user_id': int(user_id),
                    'value': value
                })
        
        # Sort by value in descending order
        leaderboard.sort(key=lambda x: x['value'], reverse=True)
        return leaderboard[:limit]
    
    def create_game_state(self, game_id: str, game_data: dict) -> GameState:
        """Create a new game state"""
        self.game_states[game_id] = game_data
        return GameState(game_data, game_id)
    
    def get_game_state(self, game_id: str) -> Optional[GameState]:
        """Get game state by ID"""
        if game_id in self.game_states:
            return GameState(self.game_states[game_id], game_id)
        return None
    
    def delete_game_state(self, game_id: str):
        """Delete a game state"""
        if game_id in self.game_states:
            del self.game_states[game_id]
