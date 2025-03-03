class User:
    def __init__(self, userid: int, username: str, messages: int = 0, voicetime: int = 0, jailed: int = 0):
        self.userid = userid
        self.username = username
        self.messages = messages
        self.voicetime = voicetime
        self.jailed = jailed