from fastapi import Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

# Обработка GET-запроса на главную страницу
async def get_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Обработка GET-запроса на аутентификацию
async def get_auth(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})

# Обработка GET-запроса на чат
async def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# Обработка POST-запроса
async def submit_form(data: str):
    return {"message": data}

# Обработка WebSocket подключений
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