from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import aiohttp

app = FastAPI(title="PARTA Admin")
templates = Jinja2Templates(directory="admin_panel/templates")  # Обновленный путь


@app.get("/")
async def admin_dashboard(request: Request):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/users") as resp:
                if resp.status != 200:
                    return {"error": f"API вернул статус {resp.status}"}
                users = await resp.json()
        return templates.TemplateResponse(
            "index.html", {"request": request, "users": users}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": str(e), "users": []}
        )


if __name__ == "__main__":
    print("Запускаем админку...")
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
