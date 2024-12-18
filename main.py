import json

import uvicorn
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List

import DB
import Data
import JWTUtils
from app.auth import router as auth_router
from app.clientapi import router as clientapi_router
# from endpoints import get_root, get_auth, get_chat, submit_form, websocket_endpoint  # Импортируем обработчики
from datetime import datetime, timedelta
import asyncio

app = FastAPI()

# Подключение статических файлов (например, CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")
app.include_router(auth_router, prefix="/auth", tags=["products"])
app.include_router(clientapi_router, prefix="/clientapi", tags=["products"])


# Список активных подключений WebSocket
# active_connections: List[WebSocket] = []

async def broadcast_message(message: str, chat_uuid: str, user_uuid: str):
    chat = await DB.db.chats.find_one({"UUID": chat_uuid})
    if chat:
        member_uuids = chat.get("member_uuids", [])
        if user_uuid in member_uuids:
            for uuid, connection in Data.websocketConnections.items():
                if uuid in member_uuids:
                    await connection.send_text(message)

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
    return templates.TemplateResponse("chat.html", {"request": request, "websocket_address": '''<script>
        const websocketAddress = "ws://127.0.0.1:8000/ws";
    </script>'''})


# Обработка POST-запроса
@app.post("/submit")
async def submit_form(data: str):
    return {"message": data}


async def handle_disconnect(websocket: WebSocket, uuid: str = None):
    if uuid:
        del Data.websocketConnections[uuid]
    elif websocket in Data.unknownConnections:
        Data.unknownConnections.remove(websocket)


# Обработка WebSocket подключений
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    Data.unknownConnections.append(websocket)
    last_jwt_check = datetime.now()
    current_uuid = None

    try:
        while True:
            try:
                # Проверяем, прошло ли 5 минут с последней проверки JWT
                if datetime.now() - last_jwt_check > timedelta(seconds=300):
                    if current_uuid:
                        await websocket.send_json({"type": "JWT_CHECK"})
                elif datetime.now() - last_jwt_check > timedelta(seconds=360):
                    await websocket.close(4001, json.dumps({"type": "ERROR", "message": "JWT was not provided"}))

                try:
                    message = await websocket.receive_json()

                    if "JWT" in message.keys():
                        try:
                            # Валидируем JWT и получаем UUID
                            validation_result = JWTUtils.validate_token(message["JWT"])
                            uuid = validation_result["UUID"]

                            if current_uuid and uuid != current_uuid:
                                await handle_disconnect(websocket, current_uuid)
                                await websocket.close(4001, json.dumps({"Type": "ERROR", "message": "Invalid JWT"}))

                                return

                            if not current_uuid:
                                # Первая авторизация
                                Data.unknownConnections.remove(websocket)
                                Data.websocketConnections[uuid] = websocket
                                current_uuid = uuid

                            last_jwt_check = datetime.now()

                        except Exception as e:
                            await handle_disconnect(websocket, current_uuid)
                            await websocket.close(4001, json.dumps({"type": "ERROR", "message": "JWT check error"}))
                            return

                    # Здесь обработка других сообщений от клиента
                    else:
                        if not current_uuid:
                            await websocket.send_json({"type": "ERROR",
                                                       "message": "Чел, мы вообще понятия не имеем кто ты. "
                                                                  "Вышли какую-нибудь телеграмму по этому "
                                                                  "сокету в формате JSON с валидным JWT в "
                                                                  "поле JWT. Получить его можно на "
                                                                  "эндпоинтах /auth, например /auth/login. "
                                                                  "Не забывай обновлять JWT не реже раз в "
                                                                  "~40 минут."})
                            continue
                        # Обработка сообщения авторизованного пользователя
                        if message["type"] == "SEND_MESSAGE":
                            chat_uuid = message["chat_uuid"]
                            user_uuid = current_uuid
                            
                            # Проверяем, есть ли пользователь в чате
                            chat = await DB.db.chats.find_one({"UUID": chat_uuid, "member_uuids": user_uuid})
                            if not chat:
                                await websocket.send_json({"type": "ERROR", "message": "Вы не состоите в этом чате."})
                                continue
                            
                            message_data = DB.schema({"content": message["content"], "chat": chat_uuid}, DB.Schemes.message)
                            await DB.db.messages.insert_one(message_data)
                            

                            # Бродкаст сообщения (оставлено в комментарии для доработки)
                            # msg = {
                            #     "type": "SEND_MESSAGE",
                            #     "chat_uuid": chat_uuid,
                            #     "content": message["content"],
                            #     "sender": user_uuid,
                            #     "timestamp": datetime.now().isoformat()
                            # }
                            await broadcast_message(message_data, chat_uuid, user_uuid)
                        print(message)
                        # await broadcast_message(message)


                except Exception as e:
                    print(f"Error processing message (in while True l1): {e}")
                await handle_disconnect(websocket, current_uuid)
                break
            except Exception as e:
                print(f"Error processing message (in while True l0): {e}")
                await handle_disconnect(websocket, current_uuid)
                break

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        await handle_disconnect(websocket, current_uuid)


async def main():
    globalChat = await DB.db.chats.find_one({"name": "Global", "isSystem": True})
    if not globalChat:
        globalChat = DB.schema({"name": "Global", "isSystem": True}, DB.Schemes.chat)
        await DB.db.chats.insert_one(globalChat)
    Data.globalChatUUID = globalChat["UUID"]



# asyncio.run(main())
if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8001)
    asyncio.run(main())

