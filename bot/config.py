import json

class Config:
    @classmethod
    def bot_token(cls):
        return cls.js['bot_token']

    @classmethod
    def db_path(cls):
        return cls.js['database_path']

    def load():
        f = open('config.conf', 'r')
        js = json.load(f)
        f.close()
        return js

    js = load()