import jwt
import datetime
import os


SECRET_KEY = str(os.getenv("JWT_SECRET"))

# Функция для генерации токена
def create_token(data, expires_in=45*60):
    payload = {

        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
    }

    _data = data.copy()
    _data.update(payload)

    token = jwt.encode(_data, SECRET_KEY, algorithm='HS256')

    return token

# Функция для проверки токена
def validate_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return "Token has expired"
    except jwt.InvalidTokenError:
        return "Invalid token"
def refresh_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return create_token(payload)
    except jwt.ExpiredSignatureError:
        return "Token has expired"
    except jwt.InvalidTokenError:
        return "Invalid token"