from fastapi import Depends

async def common_dependency():
    return {"dependency": "value"}
