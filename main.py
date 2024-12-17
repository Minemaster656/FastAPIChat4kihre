from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
from app.auth import router as auth_router
# from endpoints import get_root, get_auth, get_chat, submit_form, websocket_endpoint  # Импортируем обработчики
from datetime import datetime, timedelta

app = FastAPI()

# Подключение статических файлов (например, CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")
app.include_router(auth_router, prefix="/auth", tags=["products"])

# Список активных подключений WebSocket
active_connections: List[WebSocket] = []

async def broadcast_message(message: str):
    for connection in active_connections:
        await connection.send_text(message)

# Обработка GET-запроса на главную страницу
@app.get("/", response_class=HTMLResponse)
async def get_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Обработка GET-запроса на аутентификацию
@app.get("/auth", response_class=HTMLResponse)
async def get_auth(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})

# Обработка GET-запроса на чат
@app.get("/chat", response_class=HTMLResponse)
async def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# Обработка POST-запроса
@app.post("/submit")
async def submit_form(data: str):
    return {"message": data}

# Обработка WebSocket подключений
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await broadcast_message(data)
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        '''Disconnect handling'''
        active_connections.remove(websocket)
