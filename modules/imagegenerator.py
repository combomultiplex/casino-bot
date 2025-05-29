from PIL import Image, ImageDraw, ImageFont
import random
import io
import os
from typing import List, Tuple, Callable, Optional

class CasinoImageGenerator:
    """Generate visual images for casino games"""
    
    def __init__(self):
        self.card_width = 100
        self.card_height = 140
        self.slot_size = 120
        self._callback: Optional[Callable[[str, dict], None]] = None

    def set_callback(self, callback: Callable[[str, dict], None]):
        """Set a callback to be called after image generation.
        Args:
            callback: function(game_type: str, info: dict)
        """
        self._callback = callback

    def _notify(self, game_type: str, info: dict):
        if self._callback:
            self._callback(game_type, info)

    def create_slot_machine_image(self, reels: List[str], won: bool = False, multiplier: float = 1.0) -> io.BytesIO:
        """Create animated slot machine image"""
        # Create base image
        width, height = 400, 300
        img = Image.new('RGB', (width, height), color='#2C5530')
        draw = ImageDraw.Draw(img)
        
        # Draw slot machine frame
        frame_color = '#8B4513'
        draw.rectangle([20, 40, width-20, height-40], fill='#1a1a1a', outline=frame_color, width=8)
        
        # Draw title
        try:
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_medium = ImageFont.truetype("arial.ttf", 36)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        draw.text((width//2, 15), "🎰 SLOT MACHINE 🎰", fill='#FFD700', font=font_large, anchor="mt")
        
        # Draw reel slots
        slot_positions = [80, 160, 240]
        for i, (pos, symbol) in enumerate(zip(slot_positions, reels)):
            # Slot background
            slot_bg_color = '#FFD700' if won else '#333333'
            draw.rectangle([pos-50, 80, pos+50, 200], fill=slot_bg_color, outline='#8B4513', width=3)
            
            # Symbol
            draw.text((pos, 140), symbol, fill='#000000', font=font_medium, anchor="mm")
        
        # Draw result text
        result_text = "🎉 WINNER! 🎉" if won else "Try Again!"
        result_color = '#00FF00' if won else '#FF6B6B'
        draw.text((width//2, 240), result_text, fill=result_color, font=font_large, anchor="mt")
        # Draw multiplier if > 1
        if multiplier > 1:
            draw.text((width//2, 265), f"Multiplier: {multiplier}x", fill='#FFD700', font=font_large, anchor="mt")
        
        # Save to BytesIO
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        self._notify("slots", {"reels": reels, "won": won, "multiplier": multiplier})
        return img_buffer
    
    def create_blackjack_table(self, player_cards: List[Tuple[str, int]], 
                              dealer_cards: List[Tuple[str, int]], 
                              player_value: int, dealer_value: int, 
                              game_over: bool = False, multiplier: float = 1.0) -> io.BytesIO:
        """Create blackjack table visualization"""
        width, height = 600, 400
        img = Image.new('RGB', (width, height), color='#0F5132')
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 20)
            font_medium = ImageFont.truetype("arial.ttf", 16)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Draw table
        draw.ellipse([50, 50, width-50, height-50], fill='#2D5016', outline='#8B4513', width=4)
        
        # Title
        draw.text((width//2, 20), "🃏 BLACKJACK TABLE 🃏", fill='#FFD700', font=font_large, anchor="mt")
        
        # Dealer section
        draw.text((width//2, 80), "DEALER", fill='#FFFFFF', font=font_medium, anchor="mt")
        self._draw_cards(draw, dealer_cards, width//2 - len(dealer_cards)*25, 100, game_over)
        if game_over:
            draw.text((width//2, 160), f"Value: {dealer_value}", fill='#FFFFFF', font=font_medium, anchor="mt")
        else:
            draw.text((width//2, 160), f"Value: {dealer_cards[0][1]} + ?", fill='#FFFFFF', font=font_medium, anchor="mt")
        
        # Player section
        draw.text((width//2, 250), "PLAYER", fill='#FFFFFF', font=font_medium, anchor="mt")
        self._draw_cards(draw, player_cards, width//2 - len(player_cards)*25, 270, True)
        draw.text((width//2, 330), f"Value: {player_value}", fill='#FFFFFF', font=font_medium, anchor="mt")
        # Draw multiplier if > 1
        if multiplier > 1:
            draw.text((width//2, 360), f"Multiplier: {multiplier}x", fill='#FFD700', font=font_medium, anchor="mt")
        
        # Save to BytesIO
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        self._notify("blackjack", {
            "player_cards": player_cards,
            "dealer_cards": dealer_cards,
            "player_value": player_value,
            "dealer_value": dealer_value,
            "multiplier": multiplier
        })
        return img_buffer
    
    def _draw_cards(self, draw: ImageDraw, cards: List[Tuple[str, int]], 
                   start_x: int, start_y: int, show_all: bool = True):
        """Draw playing cards"""
        card_width, card_height = 50, 70
        
        for i, (card_name, value) in enumerate(cards):
            x = start_x + i * 60
            y = start_y
            
            if not show_all and i > 0:
                # Hidden card (face down)
                draw.rectangle([x, y, x+card_width, y+card_height], 
                             fill='#1a1a1a', outline='#FFFFFF', width=2)
                draw.text((x+card_width//2, y+card_height//2), "🂠", 
                         fill='#FFFFFF', anchor="mm")
            else:
                # Visible card
                card_color = '#FF0000' if card_name[0] in ['♥', '♦'] else '#000000'
                draw.rectangle([x, y, x+card_width, y+card_height], 
                             fill='#FFFFFF', outline='#000000', width=2)
                
                # Draw card symbol
                try:
                    font_small = ImageFont.truetype("arial.ttf", 12)
                except:
                    font_small = ImageFont.load_default()
                
                draw.text((x+card_width//2, y+card_height//2), card_name, 
                         fill=card_color, font=font_small, anchor="mm")
    
    def create_roulette_wheel(self, winning_number: int, prediction: str, multiplier: float = 1.0) -> io.BytesIO:
        """Create roulette wheel visualization"""
        size = 300
        img = Image.new('RGB', (size, size), color='#0F5132')
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 20)
            font_medium = ImageFont.truetype("arial.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Draw outer rim
        center = size // 2
        wheel_radius = 120
        draw.ellipse([center-wheel_radius, center-wheel_radius, 
                     center+wheel_radius, center+wheel_radius], 
                    fill='#8B4513', outline='#FFD700', width=4)
        
        # Draw inner wheel
        inner_radius = 100
        draw.ellipse([center-inner_radius, center-inner_radius, 
                     center+inner_radius, center+inner_radius], 
                    fill='#2C5530', outline='#FFD700', width=2)
        
        # Draw numbers around wheel (simplified)
        import math
        for i in range(0, 37):
            angle = (i * 360 / 37) * math.pi / 180
            x = center + int((inner_radius - 20) * math.cos(angle))
            y = center + int((inner_radius - 20) * math.sin(angle))
            
            # Highlight winning number
            if i == winning_number:
                draw.ellipse([x-12, y-12, x+12, y+12], fill='#FFD700')
            
            # Red or black numbers
            red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
            color = '#FF0000' if i in red_numbers else '#000000' if i != 0 else '#00FF00'
            
            draw.text((x, y), str(i), fill='#FFFFFF' if i == winning_number else color, 
                     font=font_medium, anchor="mm")
        
        # Draw ball on winning number
        ball_angle = (winning_number * 360 / 37) * math.pi / 180
        ball_x = center + int((inner_radius - 20) * math.cos(ball_angle))
        ball_y = center + int((inner_radius - 20) * math.sin(ball_angle))
        draw.ellipse([ball_x-5, ball_y-5, ball_x+5, ball_y+5], fill='#FFFFFF')
        
        # Draw center
        draw.ellipse([center-15, center-15, center+15, center+15], fill='#FFD700')
        
        # Draw result text
        draw.text((center, size-30), f"🎯 {winning_number}", fill='#FFD700', 
                 font=font_large, anchor="mt")
        draw.text((center, size-10), f"Bet: {prediction}", fill='#FFFFFF', 
                 font=font_medium, anchor="mt")
        # Draw multiplier if > 1
        if multiplier > 1:
            draw.text((center, size-50), f"Multiplier: {multiplier}x", fill='#FFD700', font=font_medium, anchor="mt")
        
        # Save to BytesIO
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        self._notify("roulette", {
            "winning_number": winning_number,
            "prediction": prediction,
            "multiplier": multiplier
        })
        return img_buffer
    
    def create_coinflip_image(self, result: str, prediction: str, won: bool, multiplier: float = 1.0) -> io.BytesIO:
        """Create coinflip visualization"""
        size = 300
        img = Image.new('RGB', (size, size), color='#0F5132')
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_medium = ImageFont.truetype("arial.ttf", 18)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Draw coin
        center = size // 2
        coin_radius = 80
        coin_color = '#FFD700'
        draw.ellipse([center-coin_radius, center-coin_radius, 
                     center+coin_radius, center+coin_radius], 
                    fill=coin_color, outline='#B8860B', width=5)
        
        # Draw coin face
        if result.lower() == 'heads':
            # Draw a simple crown for heads
            draw.text((center, center), "👑", font=font_large, anchor="mm")
        else:
            # Draw a simple symbol for tails
            draw.text((center, center), "🦅", font=font_large, anchor="mm")
        
        # Draw result text
        result_text = f"🎉 {result.upper()}! 🎉" if won else f"{result.upper()}"
        result_color = '#00FF00' if won else '#FFFFFF'
        draw.text((center, 50), result_text, fill=result_color, font=font_large, anchor="mt")
        
        # Draw prediction
        draw.text((center, size-50), f"You predicted: {prediction.upper()}", 
                 fill='#FFFFFF', font=font_medium, anchor="mt")
        
        # Draw outcome
        outcome_text = "YOU WIN!" if won else "YOU LOSE!"
        outcome_color = '#00FF00' if won else '#FF6B6B'
        draw.text((center, size-20), outcome_text, fill=outcome_color, 
                 font=font_large, anchor="mt")
        # Draw multiplier if > 1
        if multiplier > 1:
            draw.text((center, size-80), f"Multiplier: {multiplier}x", fill='#FFD700', font=font_medium, anchor="mt")
        
        # Save to BytesIO
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        self._notify("coinflip", {
            "result": result,
            "prediction": prediction,
            "won": won,
            "multiplier": multiplier
        })
        return img_buffer
    
    def create_crash_graph(self, current_multiplier: float, crashed: bool = False, win_multiplier: float = 1.0) -> io.BytesIO:
        """Create crash game multiplier graph"""
        width, height = 400, 300
        img = Image.new('RGB', (width, height), color='#1a1a1a')
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_medium = ImageFont.truetype("arial.ttf", 16)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Draw title
        title = "💥 CRASHED!" if crashed else "🚀 CRASH GAME"
        title_color = '#FF0000' if crashed else '#00FF00'
        draw.text((width//2, 20), title, fill=title_color, font=font_large, anchor="mt")
        
        # Draw graph background
        graph_left, graph_top = 50, 60
        graph_right, graph_bottom = width-50, height-60
        draw.rectangle([graph_left, graph_top, graph_right, graph_bottom], 
                      outline='#333333', width=2)
        
        # Draw multiplier curve (simplified)
        points = []
        max_x = 100
        for x in range(0, min(int(current_multiplier * 20), max_x)):
            # Exponential curve
            y = graph_bottom - (x * 2)
            points.append((graph_left + x * 3, y))
        
        if len(points) > 1:
            # Draw curve
            for i in range(len(points)-1):
                draw.line([points[i], points[i+1]], fill='#00FF00', width=3)
        
        # Draw current multiplier
        multiplier_text = f"{current_multiplier:.2f}x"
        draw.text((width//2, height//2), multiplier_text, 
                 fill='#FFFFFF', font=font_large, anchor="mm")
        
        # Draw status
        status = "CRASHED!" if crashed else "Flying..."
        status_color = '#FF0000' if crashed else '#00FF00'
        draw.text((width//2, height-30), status, fill=status_color, 
                 font=font_medium, anchor="mt")
        # Draw win multiplier if > 1
        if win_multiplier > 1:
            draw.text((width//2, height-55), f"Multiplier: {win_multiplier}x", fill='#FFD700', font=font_medium, anchor="mt")
        
        # Save to BytesIO
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        self._notify("crash", {
            "current_multiplier": current_multiplier,
            "crashed": crashed,
            "win_multiplier": win_multiplier
        })
        return img_buffer
    
    def create_mining_result(self, material: str, rarity: str, reward: int) -> io.BytesIO:
        """Create mining result visualization"""
        width, height = 350, 250
        img = Image.new('RGB', (width, height), color='#654321')
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 20)
            font_medium = ImageFont.truetype("arial.ttf", 16)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Draw mine background
        draw.rectangle([20, 20, width-20, height-20], fill='#2F1B14', outline='#8B4513', width=3)
        
        # Draw title
        draw.text((width//2, 35), "⛏️ MINING RESULT ⛏️", fill='#FFD700', 
                 font=font_large, anchor="mt")
        
        # Draw material found
        material_size = 60
        material_y = height//2 - 20
        draw.text((width//2, material_y), material, font=font_large, anchor="mm")
        
        # Draw rarity
        rarity_colors = {
            'common': '#CCCCCC',
            'uncommon': '#00FF00', 
            'rare': '#0080FF',
            'legendary': '#FF8000'
        }
        rarity_color = rarity_colors.get(rarity.lower(), '#FFFFFF')
        draw.text((width//2, material_y + 40), rarity.upper(), 
                 fill=rarity_color, font=font_medium, anchor="mt")
        
        # Draw value
        draw.text((width//2, height-40), f"Value: {reward:,} coins", 
                 fill='#FFD700', font=font_medium, anchor="mt")
        
        # Save to BytesIO
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        self._notify("mining", {
            "material": material,
            "rarity": rarity,
            "reward": reward
        })
        return img_buffer