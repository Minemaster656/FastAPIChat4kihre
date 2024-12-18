import hashlib
import json

from fastapi import APIRouter, Depends, Request
from starlette.responses import JSONResponse

import DB
import JWTUtils

router = APIRouter()


@router.post("/login")
async def login(request: Request):
    try:
        header_password = request.headers.get('Password')
        login = request.headers.get('Login')
        user_data = await DB.fetch_user_by_password(login, header_password)
        if user_data:
            return JSONResponse(status_code=200, content={"message": "Окей, проходи. JWT токен в одноимённом поле",
                                                          "JWT": JWTUtils.create_token({"UUID": user_data["UUID"]}),
                                                          "UUID": user_data["UUID"]})
        else:
            return JSONResponse(status_code=401,
                                content={"message": "Чел мы тя не знаем, тебе на /auth/register надо."})

    except Exception as e:
        print(e)
        return JSONResponse(status_code=400, content={"message": "Поля заполни нормально. В хедерах Password и Login с "
                                                                 "соответствующим контентом. В ответе JWT: жевете токен, храни его в безопасности. Сдохнет он через пол пары, минут 45 ему надо. Если достаточно умный, пошли его на /aurh/refresh, тебе новый дадут. Ошибка кстати " + str(e)})


@router.post("/refresh")
async def refresh(request: Request):
    try:

        jwt = request.headers.get('Authorization')


        if JWTUtils.validate_token(jwt):
            new_jwt = JWTUtils.refresh_token(jwt)
            if new_jwt.startswith("ERROR: "):
                return JSONResponse(status_code=400, content={"message": new_jwt})
            return JSONResponse(status_code=200,
                                content={"message": "Намана, токен валидный. Вот тебе новый в поле JWT",
                                         "JWT": new_jwt, "UUID": JWTUtils.validate_token(jwt)["UUID"]})
        else:
            return JSONResponse(status_code=401, content={"message": "ТЫ ОПОЗДАЛ, СОНИК, `токен сдох`!"})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=400, content={
            "message": "В хедер Authorization валидный JWT засунуть забыл. Да, просто JWT. Валидный. Error: " + str(e)})


@router.post("/register")
async def register(request: Request):
    try:
        payload = await request.json()

        # Проверяем наличие всех необходимых полей
        if not all(key in payload and payload[key] for key in ["login", "password", "name"]):
            return JSONResponse(status_code=400, content={"message": "Заполни пж поля: login, password, name"})

        login = payload["login"]
        password = payload["password"]
        name = payload["name"]

        # Проверяем существует ли пользователь с таким логином
        existing_user = await DB.users.find_one({"login": login})
        if existing_user:
            return JSONResponse(status_code=409, content={
                "message": "Такой юзер уже есть. /auth/login тебе в помощь, но в этот раз без подарков!"
            })

        # Создаем нового пользователя
        doc = DB.schema({}, DB.Schemes.user)
        doc["login"] = login
        doc["name"] = name
        doc["password"] = hashlib.sha256(password.encode("utf-8")).hexdigest()
        await DB.users.insert_one(doc)

        # Возвращаем JWT токен
        return JSONResponse(status_code=200, content={
            "message": "Велкоме, юзер. Выш IP (не) отправлен ФБР. В поле JWT есть токен. Он тебе нужен. Не забудь "
                      "его обновлять на POST /auth/refresh. Логинься по POST /auth/login.",
            "JWT": JWTUtils.create_token({"UUID": doc["UUID"]}),
            "UUID": doc["UUID"]
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={
            "message": "Мпаи гнамв цлугнргещштпц уменап щьц туопраеп игшц умоаигр, сервер еггог\n" + str(e)})
@router.get("/uuid")
async def get_uuid(request: Request):
    try:
        jwt = request.headers.get('Authorization')
        payload = JWTUtils.validate_token(jwt)
        if not payload.startswith("ERROR: "):
            return JSONResponse(status_code=200, content={"UUID": payload["UUID"]})
        else:
            return JSONResponse(status_code=401, content={"message": "Токен либо сдох "})
    except Exception as e:
        print(e)
        return JSONResponse(status_code=400, content={
            "message": "Засунь валидный JWT в хедер Authorization."})