from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

class User:
    """User data model"""
    
    def __init__(self, data: dict, user_id: int, guild_id: int):
        self.user_id = user_id
        self.guild_id = guild_id
        self._data = data
    
    @property
    def balance(self) -> int:
        return self._data.get('balance', 0)
    
    @balance.setter
    def balance(self, value: int):
        self._data['balance'] = max(0, value)
    
    @property
    def crypto_balance(self) -> int:
        return self._data.get('crypto_balance', 0)
    
    @crypto_balance.setter
    def crypto_balance(self, value: int):
        self._data['crypto_balance'] = max(0, value)
    
    @property
    def experience(self) -> int:
        return self._data.get('experience', 0)
    
    @experience.setter
    def experience(self, value: int):
        self._data['experience'] = max(0, value)
        self._update_level()
    
    @property
    def level(self) -> int:
        return self._data.get('level', 1)
    
    def _update_level(self):
        """Update level based on experience"""
        # Level formula: level = floor(sqrt(experience / 100)) + 1
        import math
        new_level = math.floor(math.sqrt(self.experience / 100)) + 1
        self._data['level'] = max(1, new_level)
    
    @property
    def inventory(self) -> dict:
        return self._data.get('inventory', {})
    
    def add_item(self, item_id: str, amount: int = 1):
        """Add item to inventory"""
        if 'inventory' not in self._data:
            self._data['inventory'] = {}
        
        if item_id in self._data['inventory']:
            self._data['inventory'][item_id] += amount
        else:
            self._data['inventory'][item_id] = amount
    
    def remove_item(self, item_id: str, amount: int = 1) -> bool:
        """Remove item from inventory, returns True if successful"""
        if item_id not in self.inventory or self.inventory[item_id] < amount:
            return False
        
        self._data['inventory'][item_id] -= amount
        if self._data['inventory'][item_id] <= 0:
            del self._data['inventory'][item_id]
        
        return True
    
    @property
    def mining_data(self) -> dict:
        return self._data.get('mining', {})
    
    @property
    def mining_energy(self) -> int:
        return self.mining_data.get('energy', 100)
    
    @mining_energy.setter
    def mining_energy(self, value: int):
        if 'mining' not in self._data:
            self._data['mining'] = {}
        self._data['mining']['energy'] = max(0, min(100, value))
    
    @property
    def stats(self) -> dict:
        return self._data.get('stats', {})
    
    def update_stats(self, stat: str, value: int):
        """Update a specific stat"""
        if 'stats' not in self._data:
            self._data['stats'] = {}
        
        if stat in self._data['stats']:
            self._data['stats'][stat] += value
        else:
            self._data['stats'][stat] = value
    
    def is_on_cooldown(self, cooldown_type: str) -> bool:
        """Check if user is on cooldown for specific action"""
        cooldowns = self._data.get('cooldowns', {})
        if cooldown_type not in cooldowns:
            return False
        
        last_used = datetime.fromisoformat(cooldowns[cooldown_type])
        return datetime.now() < last_used
    
    def set_cooldown(self, cooldown_type: str, duration: timedelta):
        """Set cooldown for specific action"""
        if 'cooldowns' not in self._data:
            self._data['cooldowns'] = {}
        
        self._data['cooldowns'][cooldown_type] = (datetime.now() + duration).isoformat()
    
    def get_cooldown_remaining(self, cooldown_type: str) -> Optional[timedelta]:
        """Get remaining cooldown time"""
        if not self.is_on_cooldown(cooldown_type):
            return None
        
        cooldowns = self._data.get('cooldowns', {})
        last_used = datetime.fromisoformat(cooldowns[cooldown_type])
        return last_used - datetime.now()
    
    def has_boost(self, boost_type: str) -> bool:
        """Check if user has active boost"""
        boosts = self._data.get('boosts', {})
        if boost_type not in boosts:
            return False
        
        expires_at = datetime.fromisoformat(boosts[boost_type]['expires_at'])
        return datetime.now() < expires_at
    
    def add_boost(self, boost_type: str, duration: timedelta, multiplier: float = 1.0):
        """Add boost to user"""
        if 'boosts' not in self._data:
            self._data['boosts'] = {}
        
        self._data['boosts'][boost_type] = {
            'expires_at': (datetime.now() + duration).isoformat(),
            'multiplier': multiplier
        }
    
    def get_boost_multiplier(self, boost_type: str) -> float:
        """Get boost multiplier if active"""
        if not self.has_boost(boost_type):
            return 1.0
        
        return self._data['boosts'][boost_type]['multiplier']
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        self._data['last_seen'] = datetime.now().isoformat()
        return self._data

class Guild:
    """Guild data model"""
    
    def __init__(self, data: dict, guild_id: int):
        self.guild_id = guild_id
        self._data = data
    
    @property
    def cash_name(self) -> str:
        return self._data.get('cash_name', 'coins')
    
    @cash_name.setter
    def cash_name(self, value: str):
        self._data['cash_name'] = value
    
    @property
    def crypto_name(self) -> str:
        return self._data.get('crypto_name', 'gems')
    
    @crypto_name.setter
    def crypto_name(self, value: str):
        self._data['crypto_name'] = value
    
    @property
    def cashmoji(self) -> str:
        return self._data.get('cashmoji', '🪙')
    
    @cashmoji.setter
    def cashmoji(self, value: str):
        self._data['cashmoji'] = value
    
    @property
    def cryptomoji(self) -> str:
        return self._data.get('cryptomoji', '💎')
    
    @cryptomoji.setter
    def cryptomoji(self, value: str):
        self._data['cryptomoji'] = value
    
    @property
    def admin_ids(self) -> list:
        return self._data.get('admin_ids', [])
    
    def add_admin(self, user_id: int):
        """Add admin to guild"""
        if 'admin_ids' not in self._data:
            self._data['admin_ids'] = []
        
        if user_id not in self._data['admin_ids']:
            self._data['admin_ids'].append(user_id)
    
    def remove_admin(self, user_id: int):
        """Remove admin from guild"""
        if 'admin_ids' in self._data and user_id in self._data['admin_ids']:
            self._data['admin_ids'].remove(user_id)
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.admin_ids
    
    @property
    def channels(self) -> list:
        return self._data.get('channels', [])
    
    def set_channels(self, channels: list):
        """Set allowed channels"""
        self._data['channels'] = channels
    
    @property
    def disable_update_messages(self) -> bool:
        return self._data.get('disable_update_messages', False)
    
    @disable_update_messages.setter
    def disable_update_messages(self, value: bool):
        self._data['disable_update_messages'] = value
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return self._data

class GameState:
    """Game state model for ongoing games"""
    
    def __init__(self, data: dict, game_id: str):
        self.game_id = game_id
        self._data = data
    
    @property
    def game_type(self) -> str:
        return self._data.get('game_type', '')
    
    @property
    def players(self) -> list:
        return self._data.get('players', [])
    
    @property
    def status(self) -> str:
        return self._data.get('status', 'waiting')
    
    @status.setter
    def status(self, value: str):
        self._data['status'] = value
    
    @property
    def created_at(self) -> datetime:
        return datetime.fromisoformat(self._data.get('created_at', datetime.now().isoformat()))
    
    def get_data(self, key: str, default=None):
        """Get arbitrary data from game state"""
        return self._data.get(key, default)
    
    def set_data(self, key: str, value):
        """Set arbitrary data in game state"""
        self._data[key] = value
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return self._data
