from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.main import api_router
from app.core.config import settings

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi import Request

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Store active users {username: websocket}
active_connections = {}

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_NAME,
    version=settings.VERSION,
)

app.include_router(api_router, prefix=settings.API_V1_STR)

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/chat", response_class=HTMLResponse)
async def chat_root(request: Request):
    return templates.TemplateResponse(request, "chat.html")

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    active_connections[username] = websocket
    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message")
            receiver = data.get("to")

            if receiver in active_connections:
                await active_connections[receiver].send_json({
                    "from": username,
                    "message": message
                })
            # Also send back confirmation to sender
            await websocket.send_json({
                "from": "You",
                "message": message
            })
    except WebSocketDisconnect:
        del active_connections[username]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=5001, reload=True)
