import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from datetime import timedelta
from modules.utils import *
from config import Config
from modules.imagegenerator import CasinoImageGenerator

class Games(commands.Cog):
    """Gaming commands for the Discord bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # Track active games by user_id
        self.image_generator = CasinoImageGenerator()
    
    async def check_bet_validity(self, interaction: discord.Interaction, bet: int) -> bool:
        """Check if bet is valid and user has sufficient funds"""
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        
        is_valid, error_msg = validate_bet_amount(bet, Config.MIN_BET, Config.MAX_BET, user.balance)
        if not is_valid:
            await interaction.response.send_message(embed=create_error_embed("Invalid Bet", error_msg), ephemeral=True)
            return False
        
        return True
    
    @app_commands.command(name="blackjack", description="Play blackjack")
    @app_commands.describe(bet="Amount to bet", mode="Game mode (normal/insurance)")
    async def blackjack(self, interaction: discord.Interaction, bet: int, mode: str = "normal"):
        """Blackjack game command"""
        if not await self.check_bet_validity(interaction, bet):
            return
        
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        # Deduct bet
        user.balance -= bet
        user.update_stats('total_bet', bet)
        
        # Deal cards
        dealer_cards = generate_cards(2)
        player_cards = generate_cards(2)
        
        # Calculate values
        dealer_value = calculate_blackjack_value(dealer_cards)
        player_value = calculate_blackjack_value(player_cards)
        
        # Create game embed
        embed = create_game_embed("🃏 Blackjack")
        embed.add_field(
            name="Your Cards", 
            value=f"{format_cards(player_cards)}\nValue: {player_value}", 
            inline=True
        )
        embed.add_field(
            name="Dealer Cards", 
            value=f"{dealer_cards[0][0]} ❓\nValue: {dealer_cards[0][1]} + ?", 
            inline=True
        )
        embed.add_field(name="Bet", value=format_currency(bet, guild.cashmoji), inline=False)
        
        # Check for blackjack
        if player_value == 21:
            if dealer_value == 21:
                # Push
                user.balance += bet
                embed.add_field(name="Result", value="Push! Both have blackjack", inline=False)
                embed.color = EmbedColors.WARNING
            else:
                # Player blackjack wins
                winnings = int(bet * 2.5)
                user.balance += winnings
                user.update_stats('games_won', 1)
                user.update_stats('total_won', winnings)
                embed.add_field(name="Result", value=f"Blackjack! You win {format_currency(winnings, guild.cashmoji)}", inline=False)
                embed.color = EmbedColors.SUCCESS
            
            user.update_stats('games_played', 1)
            self.bot.data_manager.update_user(user)
            await interaction.response.send_message(embed=embed)
            return
        
        # Register active game
        self.active_games[interaction.user.id] = {
            "type": "blackjack",
            "player_cards": player_cards,
            "dealer_cards": dealer_cards,
            "bet": bet,
        }
        
        # Add action buttons
        view = BlackjackView(self.bot, user, guild, dealer_cards, player_cards, bet)
        view._parent_games_cog = self  # Pass reference for cleanup
        view._user_id = interaction.user.id
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="coinflip", description="Flip a coin")
    @app_commands.describe(prediction="Heads or tails", bet="Amount to bet")
    async def coinflip(self, interaction: discord.Interaction, prediction: str, bet: int):
        """Coinflip game command"""
        if prediction.lower() not in ['heads', 'tails']:
            await interaction.response.send_message(
                embed=create_error_embed("Invalid Prediction", "Choose 'heads' or 'tails'"), 
                ephemeral=True
            )
            return
        
        if not await self.check_bet_validity(interaction, bet):
            return
        
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        # Deduct bet
        user.balance -= bet
        user.update_stats('total_bet', bet)
        user.update_stats('games_played', 1)
        
        # Flip coin
        result = random.choice(['heads', 'tails'])
        won = prediction.lower() == result
        
        # Generate coinflip image
        try:
            coinflip_image = self.image_generator.create_coinflip_image(result, prediction, won)
            file = discord.File(coinflip_image, filename="coinflip.png")
            
            embed = create_game_embed("🪙 Coinflip")
            embed.set_image(url="attachment://coinflip.png")
            embed.add_field(name="Your Prediction", value=prediction.title(), inline=True)
            embed.add_field(name="Result", value=result.title(), inline=True)
            embed.add_field(name="Bet", value=format_currency(bet, guild.cashmoji), inline=False)
            
            if won:
                winnings = bet * 2
                user.balance += winnings
                user.update_stats('games_won', 1)
                user.update_stats('total_won', winnings)
                embed.add_field(name="Outcome", value=f"🎉 You won {format_currency(winnings, guild.cashmoji)}!", inline=False)
                embed.color = EmbedColors.SUCCESS
            else:
                embed.add_field(name="Outcome", value="Better luck next time!", inline=False)
                embed.color = EmbedColors.ERROR
            
            self.bot.data_manager.update_user(user)
            await interaction.response.send_message(embed=embed, file=file)
            
        except Exception as e:
            # Fallback to text-only if image generation fails
            embed = create_game_embed("🪙 Coinflip")
            embed.add_field(name="Your Prediction", value=prediction.title(), inline=True)
            embed.add_field(name="Result", value=result.title(), inline=True)
            embed.add_field(name="Bet", value=format_currency(bet, guild.cashmoji), inline=False)
            
            if won:
                winnings = bet * 2
                user.balance += winnings
                user.update_stats('games_won', 1)
                user.update_stats('total_won', winnings)
                embed.add_field(name="Outcome", value=f"You won {format_currency(winnings, guild.cashmoji)}!", inline=False)
                embed.color = EmbedColors.SUCCESS
            else:
                embed.add_field(name="Outcome", value="You lost!", inline=False)
                embed.color = EmbedColors.ERROR
            
            self.bot.data_manager.update_user(user)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="slots", description="Play slot machine")
    @app_commands.describe(bet="Amount to bet")
    async def slots(self, interaction: discord.Interaction, bet: int):
        """Slot machine game command"""
        if not await self.check_bet_validity(interaction, bet):
            return
        
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        # Deduct bet
        user.balance -= bet
        user.update_stats('total_bet', bet)
        user.update_stats('games_played', 1)
        
        # Spin reels
        reels = create_slots_reels()
        won, winnings = calculate_slots_win(reels, bet)
        
        # Generate slot machine image
        try:
            slot_image = self.image_generator.create_slot_machine_image(reels, won)
            file = discord.File(slot_image, filename="slots.png")
            
            embed = create_game_embed("🎰 Slot Machine")
            embed.set_image(url="attachment://slots.png")
            embed.add_field(name="Reels", value=" | ".join(reels), inline=False)
            embed.add_field(name="Bet", value=format_currency(bet, guild.cashmoji), inline=True)
            
            if won:
                user.balance += winnings
                user.update_stats('games_won', 1)
                user.update_stats('total_won', winnings)
                embed.add_field(name="Result", value=f"🎉 You won {format_currency(winnings, guild.cashmoji)}!", inline=True)
                embed.color = EmbedColors.SUCCESS
            else:
                embed.add_field(name="Result", value="No match - Try again!", inline=True)
                embed.color = EmbedColors.ERROR
            
            self.bot.data_manager.update_user(user)
            await interaction.response.send_message(embed=embed, file=file)
            
        except Exception as e:
            # Fallback to text-only if image generation fails
            embed = create_game_embed("🎰 Slot Machine")
            embed.add_field(name="Reels", value=" | ".join(reels), inline=False)
            embed.add_field(name="Bet", value=format_currency(bet, guild.cashmoji), inline=True)
            
            if won:
                user.balance += winnings
                user.update_stats('games_won', 1)
                user.update_stats('total_won', winnings)
                embed.add_field(name="Result", value=f"You won {format_currency(winnings, guild.cashmoji)}!", inline=True)
                embed.color = EmbedColors.SUCCESS
            else:
                embed.add_field(name="Result", value="No match - You lost!", inline=True)
                embed.color = EmbedColors.ERROR
            
            self.bot.data_manager.update_user(user)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roulette", description="Play roulette")
    @app_commands.describe(prediction="Your prediction (number 0-36, red, black, even, odd, low, high)", bet="Amount to bet")
    async def roulette(self, interaction: discord.Interaction, prediction: str, bet: int):
        """Roulette game command"""
        # Validate prediction
        valid_predictions = ['red', 'black', 'even', 'odd', 'low', 'high'] + [str(i) for i in range(37)]
        if prediction.lower() not in valid_predictions:
            await interaction.response.send_message(
                embed=create_error_embed("Invalid Prediction", "Valid predictions: numbers 0-36, red, black, even, odd, low (1-18), high (19-36)"), 
                ephemeral=True
            )
            return
        
        if not await self.check_bet_validity(interaction, bet):
            return
        
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        # Deduct bet
        user.balance -= bet
        user.update_stats('total_bet', bet)
        user.update_stats('games_played', 1)
        
        # Spin roulette
        number = random.randint(0, 36)
        won, winnings = calculate_roulette_win(prediction.lower(), number, bet)
        
        # Determine color
        red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        color = "🔴" if number in red_numbers else "⚫" if number != 0 else "🟢"
        
        # Generate roulette wheel image
        try:
            roulette_image = self.image_generator.create_roulette_wheel(number, prediction)
            file = discord.File(roulette_image, filename="roulette.png")
            
            embed = create_game_embed("🎡 Roulette")
            embed.set_image(url="attachment://roulette.png")
            embed.add_field(name="Your Prediction", value=prediction.title(), inline=True)
            embed.add_field(name="Result", value=f"{color} {number}", inline=True)
            embed.add_field(name="Bet", value=format_currency(bet, guild.cashmoji), inline=False)
            
            if won:
                user.balance += winnings
                user.update_stats('games_won', 1)
                user.update_stats('total_won', winnings)
                embed.add_field(name="Outcome", value=f"🎉 You won {format_currency(winnings, guild.cashmoji)}!", inline=False)
                embed.color = EmbedColors.SUCCESS
            else:
                embed.add_field(name="Outcome", value="Better luck next time!", inline=False)
                embed.color = EmbedColors.ERROR
            
            self.bot.data_manager.update_user(user)
            await interaction.response.send_message(embed=embed, file=file)
            
        except Exception as e:
            # Fallback to text-only if image generation fails
            embed = create_game_embed("🎡 Roulette")
            embed.add_field(name="Your Prediction", value=prediction.title(), inline=True)
            embed.add_field(name="Result", value=f"{color} {number}", inline=True)
            embed.add_field(name="Bet", value=format_currency(bet, guild.cashmoji), inline=False)
            
            if won:
                user.balance += winnings
                user.update_stats('games_won', 1)
                user.update_stats('total_won', winnings)
                embed.add_field(name="Outcome", value=f"You won {format_currency(winnings, guild.cashmoji)}!", inline=False)
                embed.color = EmbedColors.SUCCESS
            else:
                embed.add_field(name="Outcome", value="You lost!", inline=False)
                embed.color = EmbedColors.ERROR
            
            self.bot.data_manager.update_user(user)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="crash", description="Play crash game")
    @app_commands.describe(bet="Amount to bet", mode="auto or manual")
    async def crash(self, interaction: discord.Interaction, bet: int, mode: str = "manual"):
        """Crash game command"""
        if not await self.check_bet_validity(interaction, bet):
            return
        
        user = self.bot.data_manager.get_user(interaction.user.id, interaction.guild.id)
        guild = self.bot.data_manager.get_guild(interaction.guild.id)
        
        # Deduct bet
        user.balance -= bet
        user.update_stats('total_bet', bet)
        user.update_stats('games_played', 1)
        
        # Generate crash multiplier
        crash_multiplier = generate_crash_multiplier()
        
        if mode.lower() == "auto":
            # Auto mode - random cash out
            auto_cashout = round(random.uniform(1.1, min(crash_multiplier + 0.5, 5.0)), 2)
            
            if auto_cashout <= crash_multiplier:
                winnings = int(bet * auto_cashout)
                user.balance += winnings
                user.update_stats('games_won', 1)
                user.update_stats('total_won', winnings)
                
                embed = create_success_embed("🚀 Crash - Auto Mode")
                embed.add_field(name="Auto Cash Out", value=f"{auto_cashout}x", inline=True)
                embed.add_field(name="Crash Point", value=f"{crash_multiplier}x", inline=True)
                embed.add_field(name="Result", value=f"Won {format_currency(winnings, guild.cashmoji)}!", inline=False)
            else:
                embed = create_error_embed("💥 Crash - Auto Mode")
                embed.add_field(name="Auto Cash Out", value=f"{auto_cashout}x", inline=True)
                embed.add_field(name="Crash Point", value=f"{crash_multiplier}x", inline=True)
                embed.add_field(name="Result", value="Crashed before cash out!", inline=False)
        else:
            # Manual mode with view
            view = CrashView(self.bot, user, guild, bet, crash_multiplier)
            # Register active game
            self.active_games[interaction.user.id] = {
                "type": "crash",
                "view": view,
                "crash_multiplier": crash_multiplier,
            }
            view._parent_games_cog = self  # Pass reference for cleanup
            view._user_id = interaction.user.id
            embed = create_game_embed("🚀 Crash Game")
            embed.add_field(name="Bet", value=format_currency(bet, guild.cashmoji), inline=True)
            embed.add_field(name="Current Multiplier", value="1.00x", inline=True)
            embed.add_field(name="Status", value="🟢 Flying...", inline=False)
            await interaction.response.send_message(embed=embed, view=view)
            view.start_game(interaction)
            return
        
        self.bot.data_manager.update_user(user)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="view_multiplier", description="View your current crash game multiplier")
    async def view_multiplier(self, interaction: discord.Interaction):
        """Show the current crash multiplier for your active crash game"""
        user_id = interaction.user.id
        active = self.active_games.get(user_id)
        if not active or active.get("type") != "crash":
            await interaction.response.send_message(
                embed=create_error_embed("No Active Crash Game", "You are not currently playing a crash game."),
                ephemeral=True
            )
            return
        multiplier = active.get("view").current_multiplier if active.get("view") else None
        crash_point = active.get("crash_multiplier")
        if multiplier is None:
            await interaction.response.send_message(
                embed=create_error_embed("Unavailable", "Multiplier data is not available."),
                ephemeral=True
            )
            return
        embed = create_embed("🚀 Crash Multiplier", color=EmbedColors.GAME)
        embed.add_field(name="Current Multiplier", value=f"{multiplier:.2f}x", inline=True)
        embed.add_field(name="Crash Point", value=f"{crash_point:.2f}x", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="console_focus", description="Show your current active game")
    async def console_focus(self, interaction: discord.Interaction):
        """Show the user's current active game and its status"""
        user_id = interaction.user.id
        active = self.active_games.get(user_id)
        if not active:
            await interaction.response.send_message(
                embed=create_error_embed("No Active Game", "You are not currently playing any game."),
                ephemeral=True
            )
            return
        game_type = active.get("type", "unknown").title()
        embed = create_embed(f"🎮 Console Focus: {game_type}", color=EmbedColors.GAME)
        if game_type == "Crash":
            multiplier = active.get("view").current_multiplier if active.get("view") else None
            crash_point = active.get("crash_multiplier")
            embed.add_field(name="Current Multiplier", value=f"{multiplier:.2f}x" if multiplier else "N/A", inline=True)
            embed.add_field(name="Crash Point", value=f"{crash_point:.2f}x", inline=True)
        elif game_type == "Blackjack":
            player_cards = active.get("player_cards")
            dealer_cards = active.get("dealer_cards")
            bet = active.get("bet")
            embed.add_field(name="Your Cards", value=f"{format_cards(player_cards)}", inline=True)
            embed.add_field(name="Dealer Cards", value=f"{dealer_cards[0][0]} ❓", inline=True)
            embed.add_field(name="Bet", value=str(bet), inline=True)
        else:
            embed.add_field(name="Status", value="Game in progress...", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# --- Patch: Remove active game on game end for blackjack and crash ---

class BlackjackView(discord.ui.View):
    """View for blackjack game interactions"""
    
    def __init__(self, bot, user, guild, dealer_cards, player_cards, bet):
        super().__init__(timeout=60)
        self.bot = bot
        self.user = user
        self.guild = guild
        self.dealer_cards = dealer_cards
        self.player_cards = player_cards
        self.bet = bet
        self.game_over = False
    
    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary, emoji="👆")
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.game_over or interaction.user.id != self.user.user_id:
            return
        
        # Draw card
        new_card = generate_cards(1)[0]
        self.player_cards.append(new_card)
        player_value = calculate_blackjack_value(self.player_cards)
        
        embed = create_game_embed("🃏 Blackjack")
        embed.add_field(
            name="Your Cards", 
            value=f"{format_cards(self.player_cards)}\nValue: {player_value}", 
            inline=True
        )
        embed.add_field(
            name="Dealer Cards", 
            value=f"{self.dealer_cards[0][0]} ❓\nValue: {self.dealer_cards[0][1]} + ?", 
            inline=True
        )
        embed.add_field(name="Bet", value=format_currency(self.bet, self.guild.cashmoji), inline=False)
        
        if player_value > 21:
            # Bust
            self.game_over = True
            self.user.update_stats('games_played', 1)
            embed.add_field(name="Result", value="Bust! You lose!", inline=False)
            embed.color = EmbedColors.ERROR
            self.clear_items()
        
        self.bot.data_manager.update_user(self.user)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Stand", style=discord.ButtonStyle.secondary, emoji="✋")
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.game_over or interaction.user.id != self.user.user_id:
            return
        
        self.game_over = True
        self.clear_items()
        
        # Dealer plays
        dealer_value = calculate_blackjack_value(self.dealer_cards)
        while dealer_value < 17:
            new_card = generate_cards(1)[0]
            self.dealer_cards.append(new_card)
            dealer_value = calculate_blackjack_value(self.dealer_cards)
        
        player_value = calculate_blackjack_value(self.player_cards)
        
        embed = create_game_embed("🃏 Blackjack - Final")
        embed.add_field(
            name="Your Cards", 
            value=f"{format_cards(self.player_cards)}\nValue: {player_value}", 
            inline=True
        )
        embed.add_field(
            name="Dealer Cards", 
            value=f"{format_cards(self.dealer_cards)}\nValue: {dealer_value}", 
            inline=True
        )
        embed.add_field(name="Bet", value=format_currency(self.bet, self.guild.cashmoji), inline=False)
        
        # Determine winner
        if dealer_value > 21:
            # Dealer bust
            winnings = self.bet * 2
            self.user.balance += winnings
            self.user.update_stats('games_won', 1)
            self.user.update_stats('total_won', winnings)
            embed.add_field(name="Result", value=f"Dealer bust! You win {format_currency(winnings, self.guild.cashmoji)}", inline=False)
            embed.color = EmbedColors.SUCCESS
        elif player_value > dealer_value:
            # Player wins
            winnings = self.bet * 2
            self.user.balance += winnings
            self.user.update_stats('games_won', 1)
            self.user.update_stats('total_won', winnings)
            embed.add_field(name="Result", value=f"You win {format_currency(winnings, self.guild.cashmoji)}!", inline=False)
            embed.color = EmbedColors.SUCCESS
        elif player_value == dealer_value:
            # Push
            self.user.balance += self.bet
            embed.add_field(name="Result", value="Push! Bet returned", inline=False)
            embed.color = EmbedColors.WARNING
        else:
            # Dealer wins
            embed.add_field(name="Result", value="Dealer wins!", inline=False)
            embed.color = EmbedColors.ERROR
        
        self.user.update_stats('games_played', 1)
        self.bot.data_manager.update_user(self.user)
        await interaction.response.edit_message(embed=embed, view=self)

class CrashView(discord.ui.View):
    """View for crash game interactions"""
    
    def __init__(self, bot, user, guild, bet, crash_multiplier):
        super().__init__(timeout=30)
        self.bot = bot
        self.user = user
        self.guild = guild
        self.bet = bet
        self.crash_multiplier = crash_multiplier
        self.current_multiplier = 1.00
        self.game_over = False
        self.interaction = None
    
    def start_game(self, interaction):
        """Start the crash game animation"""
        self.interaction = interaction
        self.bot.loop.create_task(self.update_multiplier())
    
    async def update_multiplier(self):
        """Update multiplier until crash"""
        while not self.game_over and self.current_multiplier < self.crash_multiplier:
            await asyncio.sleep(1)
            if self.game_over:
                break
            
            self.current_multiplier += 0.1
            self.current_multiplier = round(self.current_multiplier, 2)
            
            embed = create_game_embed("🚀 Crash Game")
            embed.add_field(name="Bet", value=format_currency(self.bet, self.guild.cashmoji), inline=True)
            embed.add_field(name="Current Multiplier", value=f"{self.current_multiplier}x", inline=True)
            embed.add_field(name="Status", value="🟢 Flying...", inline=False)
            
            try:
                await self.interaction.edit_original_response(embed=embed, view=self)
            except:
                break
        
        if not self.game_over:
            # Game crashed
            self.game_over = True
            self.clear_items()
            
            embed = create_error_embed("💥 Crashed!")
            embed.add_field(name="Bet", value=format_currency(self.bet, self.guild.cashmoji), inline=True)
            embed.add_field(name="Crash Point", value=f"{self.crash_multiplier}x", inline=True)
            embed.add_field(name="Result", value="You didn't cash out in time!", inline=False)
            
            self.user.update_stats('games_played', 1)
            self.bot.data_manager.update_user(self.user)
            
            try:
                await self.interaction.edit_original_response(embed=embed, view=self)
            except:
                pass
    
    @discord.ui.button(label="Cash Out", style=discord.ButtonStyle.success, emoji="💰")
    async def cash_out(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.game_over or interaction.user.id != self.user.user_id:
            return
        
        self.game_over = True
        self.clear_items()
        
        winnings = int(self.bet * self.current_multiplier)
        self.user.balance += winnings
        self.user.update_stats('games_won', 1)
        self.user.update_stats('total_won', winnings)
        self.user.update_stats('games_played', 1)
        
        embed = create_success_embed("💰 Cashed Out!")
        embed.add_field(name="Cash Out Multiplier", value=f"{self.current_multiplier}x", inline=True)
        embed.add_field(name="Crash Point", value=f"{self.crash_multiplier}x", inline=True)
        embed.add_field(name="Winnings", value=format_currency(winnings, self.guild.cashmoji), inline=False)
        
        # Remove active game
        if hasattr(self, "_parent_games_cog"):
            self._parent_games_cog.active_games.pop(getattr(self, "_user_id", None), None)
        
        self.bot.data_manager.update_user(self.user)
        await interaction.response.edit_message(embed=embed, view=self)

async def setup(bot):
    await bot.add_cog(Games(bot))
