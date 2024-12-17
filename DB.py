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


def schema(document, scheme):
    fields = {}
    if scheme == Schemes.message:
        fields = {"UUID": None, "content": None, "sender": None, "timestamp": None}

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
