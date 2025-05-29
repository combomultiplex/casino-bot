import os

class Config:
    """Configuration class for the Discord bot"""
    
    # Bot settings
    BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', '')
    
    # Economy settings
    DAILY_REWARD = 1000
    WEEKLY_REWARD = 5000
    MONTHLY_REWARD = 15000
    YEARLY_REWARD = 50000
    WORK_MIN_REWARD = 100
    WORK_MAX_REWARD = 500
    OVERTIME_MULTIPLIER = 1.5
    
    # Mining settings
    MINING_BASE_REWARD = 50
    MINING_ENERGY_COST = 10
    MINING_MAX_ENERGY = 100
    ENERGY_REGEN_RATE = 1  # Energy per minute
    
    # Game settings
    MIN_BET = 10
    MAX_BET = 10000
    HOUSE_EDGE = 0.02  # 2% house edge
    
    # Cooldowns (in seconds)
    DAILY_COOLDOWN = 86400  # 24 hours
    WEEKLY_COOLDOWN = 604800  # 7 days
    MONTHLY_COOLDOWN = 2592000  # 30 days
    YEARLY_COOLDOWN = 31536000  # 365 days
    WORK_COOLDOWN = 3600  # 1 hour
    OVERTIME_COOLDOWN = 14400  # 4 hours
    MINING_COOLDOWN = 300  # 5 minutes
    
    # Boost settings
    BOOST_MULTIPLIERS = {
        'experience': 2.0,
        'money': 1.5,
        'mining': 1.75,
        'luck': 1.25
    }
    
    # Prestige settings
    PRESTIGE_REQUIREMENTS = {
        'money': 1000000,
        'mining': 500000,
        'games': 100000
    }
    
    # Default guild settings
    DEFAULT_GUILD_CONFIG = {
        'cash_name': 'coins',
        'crypto_name': 'gems',
        'cashmoji': '🪙',
        'cryptomoji': '💎',
        'disable_update_messages': False,
        'channels': [],
        'admin_ids': []
    }
