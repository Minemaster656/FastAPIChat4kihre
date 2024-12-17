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
                                                          "JWT": JWTUtils.create_token({"UUID": user_data["UUID"]})})
        else:
            return JSONResponse(status_code=401,
                                content={"message": "Чел мы тя не знаем, тебе на /auth/register надо."})

    except Exception as e:
        print(e)
        return JSONResponse(status_code=400, content={"message": "Поля заполни нормально. В хедерах Password и Login с "
                                                                 "соответствующим контентом. В ответе JWT: жевете токен, храни его в безопасности. Сдохнет он через пол пары, минут 45 ему надо. Если достаточно умный, пошли его на /aurh/refresh, тебе новый дадут."})


@router.post("/refresh")
async def refresh(request: Request):
    try:

        jwt = request.headers.get('Authorization')


        if JWTUtils.validate_token(jwt):
            return JSONResponse(status_code=200,
                                content={"message": "Намана, токен валидный. Вот тебе новый в поле JWT",
                                         "JWT": JWTUtils.refresh_token(jwt)})
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

        if not payload["login"] or not payload["password"] or not payload["name"]:
            return JSONResponse(status_code=400, content={"message": "Заполни пж поля: login, password, name"})
        password = payload["password"]
        login = payload["login"]
        user_data = await DB.fetch_user_by_password(login, password)

        if user_data:

            return JSONResponse(status_code=401, content=json.dumps({
                "message": "Такой юзер уже есть. /auth/login тебе в помощь, но ладно так и быть, лови JWT поле JWT.",
                "JWT": JWTUtils.create_token({"UUID": user_data["UUID"]})}))
        else:

            doc = DB.schema({}, DB.Schemes.user)
            doc["login"] = login
            doc["password"] = hashlib.sha256(password.encode("utf-8")).hexdigest()
            await DB.users.insert_one(doc)

            return JSONResponse(status_code=200, content={
                "message": "Велкоме, юзер. Выш IP (не) отправлен ФБР. В поле JWT есть токен. Он тебе нужен. Не забудь "
                           "его обновлять на POST /auth/refresh. Логинься по POST /auth/login.",
                "JWT": JWTUtils.create_token({"UUID": doc["UUID"]})})
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "message": "Мпаи гнамв цлугнргещштпц уменап щьц туопраеп игшц умоаигр, сервер еггог\n" + str(e)})
