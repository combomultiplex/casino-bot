import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, JSON, BigInteger, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    balance = Column(Integer, default=1000)
    crypto_balance = Column(Integer, default=0)
    experience = Column(Integer, default=0)
    level = Column(Integer, default=1)
    inventory = Column(JSON, default=dict)
    mining = Column(JSON, default=dict)
    stats = Column(JSON, default=dict)
    cooldowns = Column(JSON, default=dict)
    boosts = Column(JSON, default=dict)
    prestige = Column(JSON, default=dict)
    achievements = Column(JSON, default=list)
    last_seen = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    
    def __init__(self, user_id: int, guild_id: int):
        self.user_id = user_id
        self.guild_id = guild_id
        self.balance = 1000
        self.crypto_balance = 0
        self.experience = 0
        self.level = 1
        self.inventory = {}
        self.mining = {
            'energy': 100,
            'pickaxe_level': 1,
            'mined_today': 0,
            'total_mined': 0
        }
        self.stats = {
            'games_played': 0,
            'games_won': 0,
            'total_bet': 0,
            'total_won': 0
        }
        self.cooldowns = {}
        self.boosts = {}
        self.prestige = {
            'money': 0,
            'mining': 0,
            'games': 0
        }
        self.achievements = []
        self.last_seen = datetime.now()

class Guild(Base):
    __tablename__ = 'guilds'
    
    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, unique=True, nullable=False)
    cash_name = Column(String(20), default='coins')
    crypto_name = Column(String(20), default='gems')
    cashmoji = Column(String(10), default='🪙')
    cryptomoji = Column(String(10), default='💎')
    disable_update_messages = Column(Boolean, default=False)
    channels = Column(JSON, default=list)
    admin_ids = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.now)

class GameState(Base):
    __tablename__ = 'game_states'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(String(100), unique=True, nullable=False)
    game_type = Column(String(50), nullable=False)
    players = Column(JSON, default=list)
    status = Column(String(20), default='waiting')
    data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.now)

class DatabaseManager:
    """Manages PostgreSQL database operations"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Create engine
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        logging.info("Database tables created successfully")
        
        # Auto-save task
        self._auto_save_task = None
    
    def start_auto_save(self):
        """Start the auto-save task (not needed for PostgreSQL but kept for compatibility)"""
        if self._auto_save_task is None:
            self._auto_save_task = asyncio.create_task(self._auto_save())
    
    async def _auto_save(self):
        """Auto-save placeholder (PostgreSQL handles this automatically)"""
        while True:
            await asyncio.sleep(300)  # 5 minutes
            # PostgreSQL handles persistence automatically
            logging.debug("Auto-save checkpoint (PostgreSQL)")
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def initialize_user(self, user_id: int, guild_id: int) -> User:
        """Initialize a new user or return existing user"""
        session = self.get_session()
        try:
            # Check if user exists
            user = session.query(User).filter_by(user_id=user_id, guild_id=guild_id).first()
            
            if not user:
                # Create new user
                user = User(user_id=user_id, guild_id=guild_id)
                session.add(user)
                session.commit()
                logging.info(f"Created new user: {user_id} in guild {guild_id}")
            
            return user
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error initializing user: {e}")
            raise
        finally:
            session.close()
    
    def initialize_guild(self, guild_id: int) -> Guild:
        """Initialize a new guild or return existing guild"""
        session = self.get_session()
        try:
            # Check if guild exists
            guild = session.query(Guild).filter_by(guild_id=guild_id).first()
            
            if not guild:
                # Create new guild
                guild = Guild(guild_id=guild_id)
                session.add(guild)
                session.commit()
                logging.info(f"Created new guild: {guild_id}")
            
            return guild
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error initializing guild: {e}")
            raise
        finally:
            session.close()
    
    def get_user(self, user_id: int, guild_id: int) -> User:
        """Get user data"""
        return self.initialize_user(user_id, guild_id)
    
    def get_guild(self, guild_id: int) -> Guild:
        """Get guild data"""
        return self.initialize_guild(guild_id)
    
    def update_user(self, user: User):
        """Update user data in database"""
        session = self.get_session()
        try:
            # Update last_seen
            user.last_seen = datetime.now()
            
            # Merge the user object
            session.merge(user)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error updating user: {e}")
            raise
        finally:
            session.close()
    
    def update_guild(self, guild: Guild):
        """Update guild data in database"""
        session = self.get_session()
        try:
            session.merge(guild)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error updating guild: {e}")
            raise
        finally:
            session.close()
    
    def get_leaderboard(self, guild_id: int, category: str, limit: int = 10) -> List[Dict]:
        """Get leaderboard for a specific category"""
        session = self.get_session()
        try:
            if category == 'balance':
                users = session.query(User).filter_by(guild_id=guild_id).order_by(User.balance.desc()).limit(limit).all()
                return [{'user_id': u.user_id, 'value': u.balance} for u in users]
            elif category == 'crypto':
                users = session.query(User).filter_by(guild_id=guild_id).order_by(User.crypto_balance.desc()).limit(limit).all()
                return [{'user_id': u.user_id, 'value': u.crypto_balance} for u in users]
            elif category == 'level':
                users = session.query(User).filter_by(guild_id=guild_id).order_by(User.level.desc()).limit(limit).all()
                return [{'user_id': u.user_id, 'value': u.level} for u in users]
            elif category == 'mining':
                users = session.query(User).filter_by(guild_id=guild_id).all()
                # Sort by total_mined in mining data
                sorted_users = sorted(users, key=lambda u: u.mining.get('total_mined', 0), reverse=True)
                return [{'user_id': u.user_id, 'value': u.mining.get('total_mined', 0)} for u in sorted_users[:limit]]
            elif category == 'games_won':
                users = session.query(User).filter_by(guild_id=guild_id).all()
                # Sort by games_won in stats data
                sorted_users = sorted(users, key=lambda u: u.stats.get('games_won', 0), reverse=True)
                return [{'user_id': u.user_id, 'value': u.stats.get('games_won', 0)} for u in sorted_users[:limit]]
            
            return []
        except SQLAlchemyError as e:
            logging.error(f"Error getting leaderboard: {e}")
            return []
        finally:
            session.close()
    
    def create_game_state(self, game_id: str, game_data: dict) -> GameState:
        """Create a new game state"""
        session = self.get_session()
        try:
            game_state = GameState(
                game_id=game_id,
                game_type=game_data.get('game_type', ''),
                players=game_data.get('players', []),
                status=game_data.get('status', 'waiting'),
                data=game_data
            )
            session.add(game_state)
            session.commit()
            return game_state
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error creating game state: {e}")
            raise
        finally:
            session.close()
    
    def get_game_state(self, game_id: str) -> Optional[GameState]:
        """Get game state by ID"""
        session = self.get_session()
        try:
            return session.query(GameState).filter_by(game_id=game_id).first()
        except SQLAlchemyError as e:
            logging.error(f"Error getting game state: {e}")
            return None
        finally:
            session.close()
    
    def delete_game_state(self, game_id: str):
        """Delete a game state"""
        session = self.get_session()
        try:
            game_state = session.query(GameState).filter_by(game_id=game_id).first()
            if game_state:
                session.delete(game_state)
                session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error deleting game state: {e}")
            raise
        finally:
            session.close()
    
    def save_all(self):
        """Save all data (no-op for PostgreSQL but kept for compatibility)"""
        # PostgreSQL automatically saves changes
        pass