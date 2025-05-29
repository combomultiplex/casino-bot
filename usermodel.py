from datetime import datetime, timedelta
from typing import Optional
import math
from database import DatabaseManager, User as DBUser, Guild as DBGuild
from config import Config

class UserModel:
    """User model wrapper for compatibility with existing code"""
    
    def __init__(self, db_user: DBUser, db_manager: DatabaseManager):
        self._db_user = db_user
        self._db_manager = db_manager
    
    @property
    def user_id(self) -> int:
        return self._db_user.user_id
    
    @property
    def guild_id(self) -> int:
        return self._db_user.guild_id
    
    @property
    def balance(self) -> int:
        return self._db_user.balance
    
    @balance.setter
    def balance(self, value: int):
        self._db_user.balance = max(0, value)
    
    @property
    def crypto_balance(self) -> int:
        return self._db_user.crypto_balance
    
    @crypto_balance.setter
    def crypto_balance(self, value: int):
        self._db_user.crypto_balance = max(0, value)
    
    @property
    def experience(self) -> int:
        return self._db_user.experience
    
    @experience.setter
    def experience(self, value: int):
        self._db_user.experience = max(0, value)
        self._update_level()
    
    @property
    def level(self) -> int:
        return self._db_user.level
    
    def _update_level(self):
        """Update level based on experience"""
        new_level = math.floor(math.sqrt(self.experience / 100)) + 1
        self._db_user.level = max(1, new_level)
    
    @property
    def inventory(self) -> dict:
        return self._db_user.inventory or {}
    
    def add_item(self, item_id: str, amount: int = 1):
        """Add item to inventory"""
        if not self._db_user.inventory:
            self._db_user.inventory = {}
        
        if item_id in self._db_user.inventory:
            self._db_user.inventory[item_id] += amount
        else:
            self._db_user.inventory[item_id] = amount
    
    def remove_item(self, item_id: str, amount: int = 1) -> bool:
        """Remove item from inventory, returns True if successful"""
        if not self._db_user.inventory or item_id not in self._db_user.inventory:
            return False
        
        if self._db_user.inventory[item_id] < amount:
            return False
        
        self._db_user.inventory[item_id] -= amount
        if self._db_user.inventory[item_id] <= 0:
            del self._db_user.inventory[item_id]
        
        return True
    
    @property
    def mining_data(self) -> dict:
        return self._db_user.mining or {}
    
    @property
    def mining_energy(self) -> int:
        return self.mining_data.get('energy', 100)
    
    @mining_energy.setter
    def mining_energy(self, value: int):
        if not self._db_user.mining:
            self._db_user.mining = {}
        self._db_user.mining['energy'] = max(0, min(100, value))
    
    @property
    def stats(self) -> dict:
        return self._db_user.stats or {}
    
    def update_stats(self, stat: str, value: int):
        """Update a specific stat"""
        if not self._db_user.stats:
            self._db_user.stats = {}
        
        if stat in self._db_user.stats:
            self._db_user.stats[stat] += value
        else:
            self._db_user.stats[stat] = value
    
    def is_on_cooldown(self, cooldown_type: str) -> bool:
        """Check if user is on cooldown for specific action"""
        if not self._db_user.cooldowns:
            return False
        
        if cooldown_type not in self._db_user.cooldowns:
            return False
        
        last_used = datetime.fromisoformat(self._db_user.cooldowns[cooldown_type])
        return datetime.now() < last_used
    
    def set_cooldown(self, cooldown_type: str, duration: timedelta):
        """Set cooldown for specific action"""
        if not self._db_user.cooldowns:
            self._db_user.cooldowns = {}
        
        self._db_user.cooldowns[cooldown_type] = (datetime.now() + duration).isoformat()
    
    def get_cooldown_remaining(self, cooldown_type: str) -> Optional[timedelta]:
        """Get remaining cooldown time"""
        if not self.is_on_cooldown(cooldown_type):
            return None
        
        last_used = datetime.fromisoformat(self._db_user.cooldowns[cooldown_type])
        return last_used - datetime.now()
    
    def has_boost(self, boost_type: str) -> bool:
        """Check if user has active boost"""
        if not self._db_user.boosts:
            return False
        
        if boost_type not in self._db_user.boosts:
            return False
        
        expires_at = datetime.fromisoformat(self._db_user.boosts[boost_type]['expires_at'])
        return datetime.now() < expires_at
    
    def add_boost(self, boost_type: str, duration: timedelta, multiplier: float = 1.0):
        """Add boost to user"""
        if not self._db_user.boosts:
            self._db_user.boosts = {}
        
        self._db_user.boosts[boost_type] = {
            'expires_at': (datetime.now() + duration).isoformat(),
            'multiplier': multiplier
        }
    
    def get_boost_multiplier(self, boost_type: str) -> float:
        """Get boost multiplier if active"""
        if not self.has_boost(boost_type):
            return 1.0
        
        return self._db_user.boosts[boost_type]['multiplier']

class GuildModel:
    """Guild model wrapper for compatibility with existing code"""
    
    def __init__(self, db_guild: DBGuild, db_manager: DatabaseManager):
        self._db_guild = db_guild
        self._db_manager = db_manager
    
    @property
    def guild_id(self) -> int:
        return self._db_guild.guild_id
    
    @property
    def cash_name(self) -> str:
        return self._db_guild.cash_name
    
    @cash_name.setter
    def cash_name(self, value: str):
        self._db_guild.cash_name = value
    
    @property
    def crypto_name(self) -> str:
        return self._db_guild.crypto_name
    
    @crypto_name.setter
    def crypto_name(self, value: str):
        self._db_guild.crypto_name = value
    
    @property
    def cashmoji(self) -> str:
        return self._db_guild.cashmoji
    
    @cashmoji.setter
    def cashmoji(self, value: str):
        self._db_guild.cashmoji = value
    
    @property
    def cryptomoji(self) -> str:
        return self._db_guild.cryptomoji
    
    @cryptomoji.setter
    def cryptomoji(self, value: str):
        self._db_guild.cryptomoji = value
    
    @property
    def admin_ids(self) -> list:
        return self._db_guild.admin_ids or []
    
    def add_admin(self, user_id: int):
        """Add admin to guild"""
        if not self._db_guild.admin_ids:
            self._db_guild.admin_ids = []
        
        if user_id not in self._db_guild.admin_ids:
            self._db_guild.admin_ids.append(user_id)
    
    def remove_admin(self, user_id: int):
        """Remove admin from guild"""
        if self._db_guild.admin_ids and user_id in self._db_guild.admin_ids:
            self._db_guild.admin_ids.remove(user_id)
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.admin_ids
    
    @property
    def channels(self) -> list:
        return self._db_guild.channels or []
    
    def set_channels(self, channels: list):
        """Set allowed channels"""
        self._db_guild.channels = channels
    
    @property
    def disable_update_messages(self) -> bool:
        return self._db_guild.disable_update_messages
    
    @disable_update_messages.setter
    def disable_update_messages(self, value: bool):
        self._db_guild.disable_update_messages = value