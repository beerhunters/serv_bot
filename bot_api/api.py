import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from pathlib import Path

# Добавляем корень проекта в sys.path
sys.path.append(str(Path(__file__).parent.parent))

from tgbot.database.requests import get_all_users

# from tgbot.database.requests import get_all_users

app = FastAPI(title="PARTA Bot API")

# Добавляем CORS для доступа с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Можно ограничить до конкретных доменов, например ["http://localhost:8001"]
    allow_credentials=True,  # Разрешить отправку cookies и заголовков авторизации
    allow_methods=["*"],  # Разрешить все методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)


@app.get("/users")
async def get_users():
    users = await get_all_users()
    return [
        {
            "id": user.id,
            "name": user.name.encode().decode("utf-8"),  # Принудительная перекодировка
            "tg_id": user.tg_id,
        }
        for user in users
    ]


async def run_api():
    config = Config(app=app, host="0.0.0.0", port=8000, loop="asyncio")
    server = Server(config)
    await server.serve()


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_api())
