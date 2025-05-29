import random
import discord
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import asyncio

class EmbedColors:
    """Discord embed color constants"""
    SUCCESS = 0x00ff00
    ERROR = 0xff0000
    WARNING = 0xffff00
    INFO = 0x0099ff
    GAME = 0x9966cc
    ECONOMY = 0xffd700
    MINING = 0x8b4513

def format_currency(amount: int, emoji: str = "🪙") -> str:
    """Format currency with emoji and thousands separator"""
    return f"{emoji} {amount:,}"

def format_time_remaining(delta: timedelta) -> str:
    """Format time remaining in human readable format"""
    total_seconds = int(delta.total_seconds())
    
    if total_seconds <= 0:
        return "Ready!"
    
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 and not parts:  # Only show seconds if no larger units
        parts.append(f"{seconds}s")
    
    return " ".join(parts) if parts else "Ready!"

def create_embed(title: str, description: str = "", color: int = EmbedColors.INFO) -> discord.Embed:
    """Create a standard embed"""
    embed = discord.Embed(title=title, description=description, color=color)
    embed.timestamp = datetime.now()
    return embed

def create_error_embed(title: str, description: str = "") -> discord.Embed:
    """Create an error embed"""
    return create_embed(title, description, EmbedColors.ERROR)

def create_success_embed(title: str, description: str = "") -> discord.Embed:
    """Create a success embed"""
    return create_embed(title, description, EmbedColors.SUCCESS)

def create_game_embed(title: str, description: str = "") -> discord.Embed:
    """Create a game embed"""
    return create_embed(title, description, EmbedColors.GAME)

def generate_cards(num_cards: int = 1) -> List[Tuple[str, int]]:
    """Generate random playing cards"""
    suits = ['♠️', '♥️', '♦️', '♣️']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    deck = []
    for suit in suits:
        for i, rank in enumerate(ranks):
            value = min(i + 1, 10) if rank != 'A' else 11  # Ace is 11 initially
            deck.append((f"{rank}{suit}", value))
    
    random.shuffle(deck)
    return deck[:num_cards]

def calculate_blackjack_value(cards: List[Tuple[str, int]]) -> int:
    """Calculate blackjack hand value"""
    total = sum(card[1] for card in cards)
    aces = sum(1 for card in cards if card[0].startswith('A'))
    
    # Adjust for aces
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    
    return total

def format_cards(cards: List[Tuple[str, int]]) -> str:
    """Format cards for display"""
    return " ".join(card[0] for card in cards)

def calculate_roulette_win(prediction: str, number: int, bet: int) -> Tuple[bool, int]:
    """Calculate roulette win amount"""
    # Determine color
    red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    is_red = number in red_numbers
    is_black = number != 0 and not is_red
    is_even = number % 2 == 0 and number != 0
    is_odd = number % 2 == 1
    
    # Check prediction
    won = False
    multiplier = 0
    
    if prediction == str(number):
        won = True
        multiplier = 35  # Single number bet
    elif prediction == "red" and is_red:
        won = True
        multiplier = 1
    elif prediction == "black" and is_black:
        won = True
        multiplier = 1
    elif prediction == "even" and is_even:
        won = True
        multiplier = 1
    elif prediction == "odd" and is_odd:
        won = True
        multiplier = 1
    elif prediction == "low" and 1 <= number <= 18:
        won = True
        multiplier = 1
    elif prediction == "high" and 19 <= number <= 36:
        won = True
        multiplier = 1
    
    winnings = bet * multiplier if won else 0
    return won, winnings

def create_slots_reels() -> List[str]:
    """Generate slot machine reels"""
    symbols = ['🍒', '🍋', '🍊', '🍇', '🔔', '💎', '7️⃣']
    weights = [25, 20, 18, 15, 12, 8, 2]  # Lower weights for better symbols
    
    return random.choices(symbols, weights=weights, k=3)

def calculate_slots_win(reels: List[str], bet: int) -> Tuple[bool, int]:
    """Calculate slot machine winnings"""
    multipliers = {
        '🍒': 2,
        '🍋': 3,
        '🍊': 4,
        '🍇': 5,
        '🔔': 10,
        '💎': 25,
        '7️⃣': 50
    }
    
    # Check for three of a kind
    if reels[0] == reels[1] == reels[2]:
        symbol = reels[0]
        multiplier = multipliers.get(symbol, 1)
        return True, bet * multiplier
    
    # Check for two of a kind (smaller payout)
    if reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
        return True, bet // 2
    
    return False, 0

def generate_crash_multiplier() -> float:
    """Generate crash game multiplier"""
    # Use exponential distribution for crash multiplier
    # Higher chance of low multipliers, rare high multipliers
    base = random.random()
    if base < 0.5:
        return round(1.0 + base * 2, 2)  # 1.0 - 2.0
    elif base < 0.8:
        return round(2.0 + (base - 0.5) * 6, 2)  # 2.0 - 4.0
    elif base < 0.95:
        return round(4.0 + (base - 0.8) * 20, 2)  # 4.0 - 7.0
    else:
        return round(7.0 + (base - 0.95) * 100, 2)  # 7.0+ (very rare)

async def wait_for_reaction(bot, message: discord.Message, user: discord.User, 
                          emojis: List[str], timeout: int = 30) -> Optional[str]:
    """Wait for user reaction and return the emoji"""
    for emoji in emojis:
        await message.add_reaction(emoji)
    
    def check(reaction, reaction_user):
        return (reaction_user == user and 
                str(reaction.emoji) in emojis and 
                reaction.message.id == message.id)
    
    try:
        reaction, _ = await bot.wait_for('reaction_add', check=check, timeout=timeout)
        return str(reaction.emoji)
    except asyncio.TimeoutError:
        return None

def paginate_list(items: List, page: int, per_page: int = 10) -> Tuple[List, bool, bool]:
    """Paginate a list and return items for current page"""
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    has_previous = page > 1
    has_next = end_idx < len(items)
    
    return items[start_idx:end_idx], has_previous, has_next

def calculate_experience_reward(base_amount: int, level: int) -> int:
    """Calculate experience reward based on level"""
    return int(base_amount * (1 + level * 0.1))

def validate_bet_amount(amount: int, min_bet: int, max_bet: int, user_balance: int) -> Tuple[bool, str]:
    """Validate bet amount and return success status with error message"""
    if amount < min_bet:
        return False, f"Minimum bet is {format_currency(min_bet)}"
    
    if amount > max_bet:
        return False, f"Maximum bet is {format_currency(max_bet)}"
    
    if amount > user_balance:
        return False, "Insufficient balance"
    
    return True, ""

def create_progress_bar(current: int, maximum: int, length: int = 10) -> str:
    """Create a text progress bar"""
    if maximum == 0:
        return "█" * length
    
    filled = int((current / maximum) * length)
    empty = length - filled
    
    return "█" * filled + "░" * empty
