import hashlib

from motor.motor_asyncio import AsyncIOMotorClient
import enum
import uuid

# Подключение к MongoDB
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)

# Выбор базы данных
db = client.chat_db

# Коллекции
users = db.users
messages = db.messages


class Schemes(enum.Enum):
    message = 0
    chat = 1
    user = 2


def schema(document, scheme):
    fields = {}
    if scheme == Schemes.message:
        fields = {"UUID": None, "content": None, "sender": None, "timestamp": None, "chat": None}
    if scheme == Schemes.chat:
        fields = {"UUID": None, "messages": []}
    if scheme == Schemes.user:
        fields = {"UUID": None, "login": None, "password": None, "name": None, "tag": None, "avatar": None}
    if scheme == Schemes.chat:
        fields = {"UUID": None, "name": None, "member_uuids": [], "isSystem": False}
    fields_check = {}
    if not document:
        document = fields
    for k in fields.keys():
        fields_check[k] = False
    for k in document.keys():
        if k in fields.keys():
            fields_check[k] = True
    for k in fields_check:
        if not fields_check[k]:
            document[k] = fields[k]
            fields_check[k] = True
    if "UUID" in document.keys():
        if document["UUID"] is None:
            document["UUID"] = str(uuid.uuid4())
    return document
async def fetch_user_by_password(login, password):
    document = await users.find_one({"login": login, "password": hashlib.sha256(password.encode("utf-8")).hexdigest()})
    if document is None:
        return None
    return schema(document, Schemes.user)
async def fetch_user_by_uuid(uuid: str):
    document = await users.find_one({"UUID": uuid})
    if document is None:
        return None
    return schema(document, Schemes.user)