from .model import BaseModel
from .db import DB
from .bot import Bot

BaseModel.db.connect()
DB.populate_if_empty()
b = Bot()
b.run()