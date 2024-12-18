import hashlib
import json

import fastapi.logger
from fastapi import APIRouter, Depends, Request
from starlette.responses import JSONResponse

import DB
import Data
import JWTUtils

router = APIRouter()

@router.get("/fetchchats")
async def fetchchats(request: Request):
    # fastapi.logger.logger.info(request.headers)
    try:
        # print(request.headers)
        jwt = request.headers.get('Authorization')
        # print(jwt, JWTUtils.validate_token(jwt), JWTUtils.validate_token(jwt) is not str, sep="\n\n\n")
        print(jwt)
        payload = JWTUtils.validate_token(jwt)
        print(payload)
        # fastapi.logger.logger.info(jwt)
        if payload is not str:
            uuid = payload["UUID"]
            # user_doc = await DB.fetch_user_by_uuid(uuid)
            # фетчим из бдшки все чаты где в member_uuids есть uuid
            chats = await DB.db.chats.find({"member_uuids": uuid}).to_list()
            # globalChat = await DB.db.chats.find_one({"UUID": Data.globalChatUUID})
            # print(chats)
            # chats.append(globalChat)

            chats_list = []
            for chat in chats:
                chats_list.append({"UUID": chat["UUID"], "name": chat["name"]})
            return JSONResponse(status_code=200, content={"message": "Вот твои чатексы.",
                                                          "result": chats_list})
        else:
            return JSONResponse(status_code=401,
                                content={"message": "Ты хто? /auth/login глянь."})

    except Exception as e:
        print(e)
        return JSONResponse(status_code=400, content={"message": "В хедере Authorization JWT валидный засунь. Или мы хз, сломалось чет другое. Error: " + str(e)})
@router.get("/fetchmessages/latest")
async def fetchmessages_latest(request: Request):
    try:
        jwt = request.headers.get('Authorization')
        payload = JWTUtils.validate_token(jwt)
        
        if payload is not str:
            chat_uuid = request.query_params.get('chat_uuid')
            uuid = payload["UUID"]
            
            # Проверяем, есть ли пользователь в чате
            chat = await DB.db.chats.find_one({"UUID": chat_uuid, "member_uuids": uuid})
            if chat:
                # Получаем последние 50 сообщений из DB.db.messages
                messages = await DB.db.messages.find({"chat": chat_uuid}).sort("timestamp", -1).limit(50).to_list()
                
                return JSONResponse(status_code=200, content={"message": "Вот последние 50 сообщений.", "result": [DB.schema(msg, DB.Schemes.message) for msg in messages]})
            else:
                return JSONResponse(status_code=403, content={"message": "Ты не в этом чате."})
        else:
            return JSONResponse(status_code=401, content={"message": "Ты хто? /auth/login глянь."})

    except Exception as e:
        print(e)
        return JSONResponse(status_code=400, content={"message": "Ошибка при получении сообщений. Error: " + str(e)})