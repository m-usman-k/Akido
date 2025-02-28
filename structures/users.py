class user:
    def __init__ (self, discord_id, discord_name, discord_roles, is_jailed):
        self.discord_id = discord_id
        self.discord_name = discord_name
        self.discord_roles = discord_roles
        self.is_jailed = is_jailed
        
    def __str__ (self):
        return f'{self.discord_name} ({self.discord_id})'