from fastapi import FastAPI, HTTPException
from main import init_database, parse_and_store, close_database, session
from apscheduler.schedulers.background import BackgroundScheduler
from models import Item
from pydantic import BaseModel

app = FastAPI()
scheduler = BackgroundScheduler()


@app.on_event("startup")
async def startup_event():
    init_database()
    scheduler.add_job(parse_and_store, 'interval', hours=1)  # Запуск парсинга каждый час
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    close_database()


@app.get("/")
async def read_root():
    return {"message": "Добро пожаловать в API парсинга!"}


@app.get("/parse")
async def manual_parse():
    """Ручной запуск парсинга данных."""
    message = parse_and_store()
    return {"message": message}


class ItemUpdate(BaseModel):
    name: str
    price: int


@app.put("/items/{item_id}")
async def update_item(item_id: int, item_update: ItemUpdate):
    """Редактирование товара по его ID."""
    main_session = init_database()
    item = main_session.query(Item).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Товар не найден")

    item.name = item_update.name
    item.price = item_update.price

    main_session.commit()
    return {"message": "Товар успешно обновлён", "item": {"id": item.id, "name": item.name, "price": item.price}}


@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """Удаление товара по его ID."""
    main_session = init_database()
    item = main_session.query(Item).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Товар не найден")

    main_session.delete(item)
    main_session.commit()
    return {"message": f"Товар с ID {item_id} успешно удалён"}
