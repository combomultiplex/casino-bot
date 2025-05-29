import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from models import User, Guild, GameState

# --- Add this stub if DatabaseManager is not implemented elsewhere ---
class DatabaseManager:
    def save_all(self): pass
    def initialize_user(self, user_id, guild_id): pass
    def initialize_guild(self, guild_id): pass
    def get_user(self, user_id, guild_id): pass
    def get_guild(self, guild_id): pass
    def update_user(self, user): pass
    def update_guild(self, guild): pass
    def get_leaderboard(self, guild_id, category, limit): pass
    def create_game_state(self, game_id, game_data): pass
    def get_game_state(self, game_id): pass
    def delete_game_state(self, game_id): pass
# -------------------------------------------------------------------

class DataManager:
    """Manages all data persistence and user/guild operations using DatabaseManager"""

    def __init__(self):
        self.db = DatabaseManager()
        self._auto_save_task = None

    def start_auto_save(self):
        """Start the auto-save task (not needed for PostgreSQL but kept for compatibility)"""
        if self._auto_save_task is None:
            self._auto_save_task = asyncio.create_task(self._auto_save())

    async def _auto_save(self):
        """Auto-save placeholder (PostgreSQL handles this automatically)"""
        while True:
            await asyncio.sleep(300)  # 5 minutes
            self.save_all()

    def save_all(self):
        """Save all data (no-op for PostgreSQL)"""
        self.db.save_all()

    def initialize_user(self, user_id: int, guild_id: int) -> User:
        """Initialize a new user or return existing user"""
        return self.db.initialize_user(user_id, guild_id)

    def initialize_guild(self, guild_id: int) -> Guild:
        """Initialize a new guild or return existing guild"""
        return self.db.initialize_guild(guild_id)

    def get_user(self, user_id: int, guild_id: int) -> User:
        """Get user data"""
        return self.db.get_user(user_id, guild_id)

    def get_guild(self, guild_id: int) -> Guild:
        """Get guild data"""
        return self.db.get_guild(guild_id)

    def update_user(self, user: User):
        """Update user data in database"""
        self.db.update_user(user)

    def update_guild(self, guild: Guild):
        """Update guild data in database"""
        self.db.update_guild(guild)

    def get_leaderboard(self, guild_id: int, category: str, limit: int = 10) -> List[Dict]:
        """Get leaderboard for a specific category"""
        return self.db.get_leaderboard(guild_id, category, limit)

    def create_game_state(self, game_id: str, game_data: dict) -> GameState:
        """Create a new game state"""
        return self.db.create_game_state(game_id, game_data)

    def get_game_state(self, game_id: str) -> Optional[GameState]:
        """Get game state by ID"""
        return self.db.get_game_state(game_id)

    def delete_game_state(self, game_id: str):
        """Delete a game state"""
        self.db.delete_game_state(game_id)
