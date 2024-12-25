from parser import get_data
from db.db import Database
from sqlalchemy.orm import sessionmaker
from models import Item
from sqlalchemy.orm import Session

session: Session = None

def init_database():
    """Инициализирует базу данных и возвращает сессию."""
    global session
    db = Database()
    db.create()

    Session = sessionmaker(bind=db.engine)
    session = Session()
    return session

def item_exists(name, price):
    """Проверяет, существует ли элемент с таким же именем и ценой в базе данных."""
    return session.query(Item).filter_by(name=name, price=price).first() is not None

def parse_and_store():
    """Парсит данные и сохраняет их в базу данных, избегая дубликатов."""
    try:
        items = get_data()
        if items:
            new_items = []
            for item in items:
                if not item_exists(item.name, item.price):
                    new_items.append(item)

            if new_items:
                session.add_all(new_items)
                session.commit()
                return f"Успешно добавлено {len(new_items)} новых элементов."
            else:
                return "Все элементы уже существуют в базе данных."
        else:
            return "Нет данных для добавления."
    except Exception as e:
        session.rollback()
        return f"Произошла ошибка: {e}"

def close_database():
    """Закрывает сессию базы данных."""
    if session:
        session.close()
