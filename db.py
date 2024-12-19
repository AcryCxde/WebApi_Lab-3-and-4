from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine


class Database:
    engine = create_engine("sqlite:///sqlite3.db")
    Base = declarative_base()

    def create(self):
        self.Base.metadata.create_all(self.engine)
