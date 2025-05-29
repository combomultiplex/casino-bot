from database import DataManager

class Economy:
    def __init__(self):
        self.data_manager = DataManager()

    def set_money(self, user_id, amount, guild_id=0):
        user = self.data_manager.get_user(user_id, guild_id)
        user.balance = amount
        self.data_manager.update_user(user)

    def set_credits(self, user_id, amount, guild_id=0):
        user = self.data_manager.get_user(user_id, guild_id)
        user.crypto_balance = amount
        self.data_manager.update_user(user)

    def add_money(self, user_id, amount, guild_id=0):
        user = self.data_manager.get_user(user_id, guild_id)
        user.balance += amount
        self.data_manager.update_user(user)

    def get_entry(self, user_id, guild_id=0):
        user = self.data_manager.get_user(user_id, guild_id)
        # Return (user_id, balance, crypto_balance)
        return (user.user_id, user.balance, user.crypto_balance)

    def top_entries(self, count=5, guild_id=0):
        leaderboard = self.data_manager.get_leaderboard(guild_id, "balance", count)
        # leaderboard is a list of dicts with 'user_id' and 'value'
        return [(entry['user_id'], entry['value']) for entry in leaderboard]
