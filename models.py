from sqlalchemy import Integer, String, Column
from datetime import datetime
from db.db import Database

def now_with_seconds():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Item(Database.Base):
    __tablename__ = 'items'
    id = Column(Integer(), primary_key=True)
    name = Column(String(), nullable=False)
    price = Column(Integer(), nullable=False)
    created_on = Column(String(), default=now_with_seconds)
    updated_on = Column(String(), default=now_with_seconds, onupdate=now_with_seconds)
