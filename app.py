from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from db.db_manager import init_database, parse_and_store, close_database
from apscheduler.schedulers.background import BackgroundScheduler
from models import Item
from pydantic import BaseModel
from templates.websocket_page import html_content


app = FastAPI()
scheduler = BackgroundScheduler()

connected_clients: list[WebSocket] = []


class ConnectionManager:
    """Управляет подключениями WebSocket."""
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


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
    """Редирект на страницу WebSocket клиента."""
    return RedirectResponse(url="/websocket-client")


@app.get("/websocket-client", response_class=HTMLResponse)
async def websocket_client():
    """Возвращает HTML-страницу с подключением к WebSocket."""
    return HTMLResponse(content=html_content)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket-соединение для уведомлений."""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Держим соединение открытым
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/parse")
async def manual_parse():
    """Ручной запуск парсинга данных."""
    message = parse_and_store()
    await manager.broadcast(f"Парсер: {message}")
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
    await manager.broadcast(f"Товар обновлён: {item.id} - {item.name}, {item.price}")
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
    await manager.broadcast(f"Товар удалён: ID {item_id}")
    return {"message": f"Товар с ID {item_id} успешно удалён"}
